from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from starlette import status

from app.domain.entities.routes import Route, RouteWorkSchedule
from app.presentation.api.decorators.only_admin import only_admin
from app.presentation.api.routes.routes.schemas import GetRouteSchema, AddRouteSchema, TotalRoutesLengthSchema, UpdateRouteSchema, PutRouteSchema
from app.services.routes import RouteService

router = APIRouter(
    prefix="/routes",
    tags=["Маршруты"],
    route_class=DishkaRoute
)


@router.get(
    "",
    summary="Получить список маршрутов",
    response_model=list[GetRouteSchema],
    status_code=status.HTTP_200_OK
)
async def get_routes(
        route_service: FromDishka[RouteService],
):
    routes = await route_service.get_routes()
    return [
        GetRouteSchema.model_validate(route, from_attributes=True)
        for route in routes
    ]


@router.get(
    '/total-length',
    summary="Получить общую длину всех маршрутов",
    response_model=TotalRoutesLengthSchema
)
async def get_total_length(
        route_service: FromDishka[RouteService],
):
    length_lm = await route_service.get_total_length()
    return TotalRoutesLengthSchema(
        total_length=length_lm
    )



@router.get(
    "/{route_id}",
    summary="Получить маршрут",
    response_model=GetRouteSchema,
    status_code=status.HTTP_200_OK
)
async def get_route(
        route_service: FromDishka[RouteService],
        route_id: int
):
    route = await route_service.get_route(route_id)
    return GetRouteSchema.model_validate(route, from_attributes=True)


@router.post(
    "",
    summary="Добавить маршрут",
    response_model=GetRouteSchema,
    status_code=status.HTTP_201_CREATED
)
@only_admin
async def add_route(
        route: AddRouteSchema,
        route_service: FromDishka[RouteService]
):
    route = await route_service.add_route(
        Route(
            id=None,
            name=route.name,
            start_point_name=route.start_point_name,
            end_point_name=route.end_point_name,
            start_time=route.start_time,
            end_time=route.end_time,
            interval_seconds=route.interval_seconds,
            duration_seconds=route.duration_seconds,
            length=route.length_km
        )
    )
    return GetRouteSchema.model_validate(route, from_attributes=True)


@router.delete(
    "/{route_id}",
    summary="Удалить маршрут",
    status_code=status.HTTP_204_NO_CONTENT
)
@only_admin
async def delete_route(
        route_id: int,
        route_service: FromDishka[RouteService]
):
    await route_service.delete_route(route_id)


@router.get(
    '/schedules',
    summary="Получить расписание для каждого маршрута",
    response_model=list[RouteWorkSchedule]
)
async def get_schedule_by_routes(
        route_service: FromDishka[RouteService],
):
    return await route_service.get_route_schedules()


@router.patch(
    "/{route_id}",
    summary="Обновить маршрут",
    response_model=GetRouteSchema,
)
@only_admin
async def update_route(
    route_id: int,
    route_update: UpdateRouteSchema,
    route_service: FromDishka[RouteService],
):
    route = await route_service.update_route(
        route_id=route_id,
        name=route_update.name,
        start_point_name=route_update.start_point_name,
        end_point_name=route_update.end_point_name,
        start_time=route_update.start_time,
        end_time=route_update.end_time,
        interval_seconds=route_update.interval_seconds,
        duration_seconds=route_update.duration_seconds,
        length_km=route_update.length_km
    )
    return GetRouteSchema.model_validate(route, from_attributes=True)


@router.put(
    "/{route_id}",
    summary="Полностью обновить маршрут",
    response_model=GetRouteSchema,
)
@only_admin
async def put_route(
    route_id: int,
    route_update: PutRouteSchema,
    route_service: FromDishka[RouteService],
):
    route = await route_service.put_route(
        route_id=route_id,
        name=route_update.name,
        start_point_name=route_update.start_point_name,
        end_point_name=route_update.end_point_name,
        start_time=route_update.start_time,
        end_time=route_update.end_time,
        interval_seconds=route_update.interval_seconds,
        duration_seconds=route_update.duration_seconds,
        length_km=route_update.length_km
    )
    return GetRouteSchema.model_validate(route, from_attributes=True)
