import asyncio

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import (
    db_helper,
    User,
    Profile,
    Post,
    Order,
    Product,
    OrderProductAssociation,
)


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


async def create_order(
    session: AsyncSession,
    promocode: str | None = None,
) -> Order:
    order = Order(promocode=promocode)
    print("Order before commit", order.id)
    session.add(order)
    await session.commit()
    print("Order after commit", order.id)
    return order


async def create_product(
    session: AsyncSession,
    name: str,
    description: str,
    price: int,
) -> Product:
    product = Product(name=name, description=description, price=price)
    print("Product before commit", product.id)
    session.add(product)
    await session.commit()
    print("Product after commit", product.id)
    return product


async def create_orders_and_products(session: AsyncSession):
    order_no_promo = await create_order(session)
    order_with_promo = await create_order(session, promocode="promo")

    book_metro_2033 = await create_product(
        session,
        "Metro 2033",
        "Post-apocalypse by Dmitry Glukhovsky in the Moscow subway",
        499,
    )
    book_metro_2034 = await create_product(
        session,
        "Metro 2034",
        "Continuation of Dmitry Glukhovsky's novel in the post apocalyptic Moscow of the future",
        459,
    )
    book_post = await create_product(
        session,
        "Post",
        "A new post-apocalypse from Dmitry Glukhovsky with the return of the monarchy and new NLP weapons",
        899,
    )

    order_no_promo = await session.scalar(
        select(Order)
        .where(Order.id == order_no_promo.id)
        .options(selectinload(Order.products))
    )

    order_with_promo = await session.scalar(
        select(Order)
        .where(Order.id == order_with_promo.id)
        .options(selectinload(Order.products))
    )

    if order_no_promo:
        order_no_promo.products.append(book_metro_2033)

    if order_with_promo:
        order_with_promo.products.append(book_metro_2033)
        order_with_promo.products.append(book_metro_2034)
        order_with_promo.products.append(book_post)

    await session.commit()


async def get_orders_with_products(session: AsyncSession) -> list[Order]:
    stmt = select(Order).options(selectinload(Order.products)).order_by(Order.id)
    orders = await session.scalars(stmt)

    return list(orders)


async def demo_get_orders_with_products_through_secondary(session: AsyncSession):
    orders = await get_orders_with_products(session=session)
    for order in orders:
        print(order.id, order.promocode, order.created_at, "products:")
        for product in order.products:  # type: ignore
            print("-", product.id, product.name, product.price)


async def get_orders_with_products_assoc(session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products_details).joinedload(
                OrderProductAssociation.product
            )
        )
        .order_by(Order.id)
    )
    orders = await session.scalars(stmt)

    return list(orders)


async def demo_get_orders_with_products_with_assoc(session: AsyncSession):
    orders = await get_orders_with_products_assoc(session=session)

    for order in orders:
        print(order.id, order.promocode, order.created_at, "products:")

        for order_product_details in order.products_details:
            print(
                "-",
                order_product_details.product.id,
                order_product_details.product.name,
                order_product_details.product.price,
                "qty:",
                order_product_details.count,
            )


async def create_gift_product_for_existing_products(session: AsyncSession):
    orders = await get_orders_with_products_assoc(session=session)
    gift_product = await create_product(
        session=session, name="Gift", description="Gift for You", price=0
    )
    for order in orders:
        order.products_details.append(
            OrderProductAssociation(
                product=gift_product,
                count=1,
                unit_price=0,
            )
        )

    await session.commit()


async def demo_m2m(session: AsyncSession):
    # await create_orders_and_products(session=session)
    # await demo_get_orders_with_products_through_secondary(session=session)
    await demo_get_orders_with_products_with_assoc(session=session)
    # await create_gift_product_for_existing_products(session=session)
    


async def main():
    async with db_helper.session_factory() as session:
        # await main_relations(session=session)
        await demo_m2m(session=session)


if __name__ == "__main__":
    asyncio.run(main())
