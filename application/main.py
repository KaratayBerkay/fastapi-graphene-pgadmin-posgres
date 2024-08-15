from email.policy import default

import graphene
import pydantic

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from starlette.graphql import GraphQLApp

from models.somemodel import Post
from models.database import db_session
from schemas import PostModel, PostSchema


db = db_session.session_factory()
app = FastAPI()

class CreateNewPostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    content = graphene.String(required=True)
    author = graphene.String(required=False)


class CreateNewPost(graphene.Mutation):
    class Arguments:
        post_data = CreateNewPostInput(required=True)

    ok = graphene.Boolean()
    post = graphene.Field(PostModel, required=False)
    message = graphene.String(required=False)

    @staticmethod
    def mutate(root, info, **kwargs):
        from sqlalchemy import func
        post = PostSchema(**kwargs.get('post_data'))
        if already_exits := db.query(Post).filter(func.lower(Post.title) == str(post.title).lower()).first():
            return CreateNewPost(
                ok=False, post=already_exits, message="Row already exits in database"
            )
        db_post = Post(**kwargs.get('post_data'))
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return CreateNewPost(
            ok=True, post=db_post, message="New post is created"
        )


class UpdateNewPost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        author = graphene.String(required=False)

    ok = graphene.Boolean()
    # found = graphene.Field(PostModel, required=False)
    post = graphene.Field(PostModel, required=False)
    message = graphene.String(required=False)

    @staticmethod
    def mutate(root, info, **kwargs):
        post = PostSchema(**kwargs)
        if db.query(Post).filter(Post.id == kwargs.get('id')).first():
            db.query(Post).filter(Post.id == kwargs.get('id')).update(post.dict())
            db.commit()
            db.flush()
            return UpdateNewPost(
                ok=True, post=Post(**kwargs), message="Row already exits in database"
            )
        return UpdateNewPost(
            ok=False, post=None, message="Id is not found in database"
        )

class DeleteNewPost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    post = graphene.Field(PostModel, required=False)
    message = graphene.String(required=False)

    @staticmethod
    def mutate(root, info, **kwargs):
        if already_exits := db.query(Post).filter(Post.id == kwargs.get('id')).first():
            db.delete(already_exits)
            db.commit()
            db.flush()
            return DeleteNewPost(
                ok=True, post=already_exits, message=f"Post with id {already_exits.id} is now deleted"
            )
        return DeleteNewPost(
            ok=False, post=None, message=f"Post with id {already_exits.id} is NOT deleted"
        )


class PostMutations(graphene.ObjectType):
    create_new_post = CreateNewPost.Field()
    update_post = UpdateNewPost.Field()
    delete_post = DeleteNewPost.Field()


class Pagination(pydantic.BaseModel):
    page: int = 1
    size: int = 3





class Query(graphene.ObjectType):

    all_posts = graphene.List(
        PostModel,
        page=graphene.Int(
            name="page",
            required=False,
            # deprecation_reason="deprecation_reason",
            default_value=1,
            description="page description"
        ),
        size=graphene.Int(
            name="size",
            required=False,
            default_value=5,
            description="size description"
        )
    )
    post_by_id = graphene.Field(
        PostModel,
        post_id=graphene.Int(required=True)
    )

    def resolve_all_posts(self, info, **kwargs):
        pagination = Pagination(**kwargs)
        query = PostModel.get_query(info).limit(pagination.size).offset((pagination.page - 1) * pagination.size)
        return query.all()

    def resolve_post_by_id(self, info, **kwargs):
        return PostModel.get_node(info, id=kwargs.get('post_id'))
        # return db.query(Post).filter(Post.id == kwargs.get('post_id')).first()

@app.get("/")
async def redirect_typer():
    return RedirectResponse("http://0.0.0.0:8000/graphql")


app.add_route("/graphql", GraphQLApp(schema=graphene.Schema(query=Query, mutation=PostMutations)))
