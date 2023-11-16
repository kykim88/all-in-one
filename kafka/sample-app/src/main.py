from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
import asyncio
from producer import Worker as Producer

# on_event deprecated -> lifespan으로 변경
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("lifespan start...")
    producer = Producer()
    task1 = asyncio.create_task(producer.process())
    logger.info("lifespan start !")
    yield
    logger.info("lifespan close...")
    task1.cancel()
    if producer:
        producer.close()
    logger.info("lifespan closed!")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get_root():
    # logger.debug("this is root!")
    return "this is root"


@app.get("/health")
async def get_health():
    return "healthy"