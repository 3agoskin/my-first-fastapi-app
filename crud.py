import asyncio

from sqlalchemy import select
from sqlalchemy.orm import joinedload
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


async def main():
    async with db_helper.session_factory() as session:
        user_yuri = await get_user_by_username(session=session, username="yuri")
        user_john = await get_user_by_username(session=session, username="john")
        if user_yuri:
            await create_posts(
                session,
                user_yuri.id,
                "New transfer to Spartak",
                "Questions for Mutko",
                "The game for jopa",
            )
        if user_john:
            await create_posts(
                session,
                user_john.id,
                "How to defeat Skynet!",
                "Don't give up",
                "Types of terminators",
            )


if __name__ == "__main__":
    asyncio.run(main())
