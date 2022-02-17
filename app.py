import uvicorn
from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from api.routes import api_router
from api.routes import api_router_v2
from config import ConfigClass

app = FastAPI(
    title="EntityInfo Service",
    description="EntityInfo",
    docs_url="/v1/api-doc",
    version="0.3.0"
)
app.add_middleware(DBSessionMiddleware, db_url=ConfigClass.RDS_DB_URI)
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def instrument_app(app) -> None:
    """Instrument the application with OpenTelemetry tracing."""

    tracer_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: ConfigClass.APP_NAME}))
    trace.set_tracer_provider(tracer_provider)

    jaeger_exporter = JaegerExporter(
        agent_host_name=ConfigClass.OPEN_TELEMETRY_HOST, agent_port=ConfigClass.OPEN_TELEMETRY_PORT
    )

    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()
    AsyncPGInstrumentor().instrument()


if ConfigClass.OPEN_TELEMETRY_ENABLED:
    instrument_app(app)

router = APIRouter()

app.include_router(api_router, prefix="/v1")
app.include_router(api_router_v2, prefix="/v2")

if __name__ == "__main__":
    uvicorn.run("app:app", host=ConfigClass.HOST, port=ConfigClass.PORT, log_level="info", reload=True)
