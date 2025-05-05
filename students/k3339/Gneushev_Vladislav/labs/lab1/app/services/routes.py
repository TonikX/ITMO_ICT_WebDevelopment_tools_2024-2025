from datetime import time

from app.domain.entities.assignments import DayOfWeek
from app.domain.entities.routes import Route, RouteWorkSchedule
from app.domain.entities.schedule import DayWorkingHours
from app.infrastructure.database.repositories.assignments import AssignmentRepository
from app.infrastructure.database.repositories.routes import RouteRepository
from app.services.exceptions import EntityNotFound


class RouteService:
    def __init__(self, route_repo: RouteRepository, assignment_repo: AssignmentRepository):
        self.route_repo = route_repo
        self.assignment_repo = assignment_repo

    async def get_routes(self) -> list[Route]:
        return await self.route_repo.get_routes()

    async def get_route(self, route_id: int) -> Route:
        route = await self.route_repo.get_route_by_id(route_id)
        if not route:
            raise EntityNotFound(
                entity=Route,
                field_name='id',
                value=route_id
            )
        return route

    async def add_route(self, route: Route) -> Route:
        return await self.route_repo.add_route(route)

    async def delete_route(self, route_id: int) -> None:
        route = await self.route_repo.get_route_by_id(route_id)
        if not route:
            raise EntityNotFound(
                entity=Route,
                field_name='id',
                value=route_id
            )
        await self.route_repo.delete_route(route_id)

    async def get_route_schedules(self) -> list[RouteWorkSchedule]:
        routes = await self.route_repo.get_routes()
        assignments = await self.assignment_repo.get_assignments(active=True)
        if not routes:
            return []

        route_schedules = {
            route.id: {day: None for day in DayOfWeek} for route in routes
        }

        for assignment in assignments:
            route_id = assignment.route.id
            day = assignment.day_of_week
            route = assignment.route

            if route_schedules[route_id][day] is None:
                route_schedules[route_id][day] = DayWorkingHours(
                    start_time=route.start_time,
                    end_time=route.end_time
                )
            else:
                existing_hours = route_schedules[route_id][day]
                route_schedules[route_id][day] = DayWorkingHours(
                    start_time=min(existing_hours.start_time, route.start_time),
                    end_time=max(existing_hours.end_time, route.end_time)
                )

        route_work_schedules = []
        for route in routes:
            schedule = route_schedules[route.id]
            route_work_schedules.append(RouteWorkSchedule(
                route=route,
                monday=schedule[DayOfWeek.monday],
                tuesday=schedule[DayOfWeek.tuesday],
                wednesday=schedule[DayOfWeek.wednesday],
                thursday=schedule[DayOfWeek.thursday],
                friday=schedule[DayOfWeek.friday],
                saturday=schedule[DayOfWeek.saturday],
                sunday=schedule[DayOfWeek.sunday]
            ))

        return route_work_schedules

    async def get_total_length(self) -> int:
        return await self.route_repo.get_total_length()

    async def update_route(
        self,
        route_id: int,
        name: str | None = None,
        start_point_name: str | None = None,
        end_point_name: str | None = None,
        start_time: time | None = None,
        end_time: time | None = None,
        interval_seconds: int | None = None,
        duration_seconds: int | None = None,
        length_km: int | None = None
    ) -> Route:
        route = await self.route_repo.get_route_by_id(route_id)
        if not route:
            raise EntityNotFound(
                entity=Route,
                field_name='id',
                value=route_id
            )

        if name is not None:
            route.name = name
        if start_point_name is not None:
            route.start_point_name = start_point_name
        if end_point_name is not None:
            route.end_point_name = end_point_name
        if start_time is not None:
            route.start_time = start_time
        if end_time is not None:
            route.end_time = end_time
        if interval_seconds is not None:
            route.interval_seconds = interval_seconds
        if duration_seconds is not None:
            route.duration_seconds = duration_seconds
        if length_km is not None:
            route.length = length_km

        return await self.route_repo.update_route(route)

    async def put_route(
        self,
        route_id: int,
        name: str,
        start_point_name: str,
        end_point_name: str,
        start_time: time,
        end_time: time,
        interval_seconds: int,
        duration_seconds: int,
        length_km: int
    ) -> Route:
        route = await self.route_repo.get_route_by_id(route_id)
        if not route:
            raise EntityNotFound(
                entity=Route,
                field_name='id',
                value=route_id
            )

        route.name = name
        route.start_point_name = start_point_name
        route.end_point_name = end_point_name
        route.start_time = start_time
        route.end_time = end_time
        route.interval_seconds = interval_seconds
        route.duration_seconds = duration_seconds
        route.length = length_km

        return await self.route_repo.update_route(route)
