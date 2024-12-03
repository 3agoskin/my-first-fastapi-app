import asyncio

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, User, Profile, Post


async def create_user(session: AsyncSession, username: str) -> User:
    user = User(username=username)
    session.add(user)
    await session.commit()
    print("user", user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    user: User | None = await session.scalar(stmt)
    print("found user", username, user)
    return user


async def create_user_profile(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    bio: str | None = None,
) -> Profile:
    profile = Profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        bio=bio,
    )
    session.add(profile)
    await session.commit()
    return profile


async def show_users_with_profiles(session: AsyncSession):  # -> list[User]:
    stmt = select(User).options(joinedload(User.profile)).order_by(User.id.desc())
    # result: Result = await session.execute(stmt)
    # users = result.scalars()
    users = await session.scalars(stmt)

    for user in users:
        print(
            user,
            ", First Name:",
            user.profile.first_name,
            ", Last Name:",
            user.profile.last_name,
            ", Bio:",
            user.profile.bio,
            sep="",
        )


async def create_posts(
    session: AsyncSession,
    user_id: int,
    *posts_titles: str,
) -> list[Post]:
    posts = [Post(title=title, user_id=user_id) for title in posts_titles]
    session.add_all(posts)
    await session.commit()
    return posts


async def get_users_with_posts(session: AsyncSession):
    # stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    stmt = select(User).options(selectinload(User.posts)).order_by(User.id)
    # users = await session.scalars(stmt)
    result: Result = await session.execute(stmt)
    users = result.scalars()

    # for user in users.unique():
    for user in users:
        print("---" * 5)
        print(user)
        for post in user.posts:
            print("  -", post)


async def get_posts_with_authors(session: AsyncSession):
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
    posts = await session.scalars(stmt)

    for post in posts:
        print("post -", post, "author -", post.user)


async def get_users_with_posts_and_profiles(session: AsyncSession):
    stmt = (
        select(User)
        .options(joinedload(User.profile), selectinload(User.posts))
        .order_by(User.id)
    )
    users = await session.scalars(stmt)

    # for user in users.unique():
    for user in users:
        print("---" * 5)
        print(user, user.profile.first_name, user.profile.last_name)
        for post in user.posts:
            print("  -", post)


async def get_profiles_with_users_and_users_with_posts(session: AsyncSession):
    stmt = (
        select(Profile)
        .join(Profile.user)
        .options(joinedload(Profile.user).selectinload(User.posts))
        .where(User.username == "john")
        .order_by(Profile.id)
    )
    profiles = await session.scalars(stmt)

    for profile in profiles:
        print("***" * 8)
        print("- profile", profile.first_name, profile.user)
        print("- posts", profile.user.posts)


async def main_relations(session: AsyncSession):
    await create_user(session=session, username="john")
    await create_user(session=session, username="alice")
    await create_user(session=session, username="sam")
    user_sam = await get_user_by_username(session=session, username="sam")
    user_john = await get_user_by_username(session=session, username="john")
    # user_bob = await get_user_by_username(session=session, username="bob")
    if user_john:
        await create_user_profile(
            session=session,
            user_id=user_john.id,
            first_name="John",
        )
        await create_posts(
            session,
            user_john.id,
            "SQLA 2.0",
            "SQLA Joins",
        )
    if user_sam:
        await create_user_profile(
            session=session,
            user_id=user_sam.id,
            first_name="Sam",
            last_name="White",
        )
        await create_posts(
            session,
            user_sam.id,
            "FastAPI intro",
            "FastAPI Advanced",
            "FastAPI more",
        )
    await show_users_with_profiles(session=session)

    await get_users_with_posts(session=session)
    await get_posts_with_authors(session=session)
    await get_users_with_posts_and_profiles(session=session)
    await get_profiles_with_users_and_users_with_posts(session=session)


async def demo_m2m(session: AsyncSession):
    pass


async def main():
    async with db_helper.session_factory() as session:
        # await main_relations(session=session)
        await demo_m2m(session=session)


if __name__ == "__main__":
    asyncio.run(main())
