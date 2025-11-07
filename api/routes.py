from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.get("/about")
async def about():
    from config.settings import APP_NAME, APP_VERSION
    return {"name": APP_NAME, "version": APP_VERSION}

@router.get("/greet/{name}")
async def greet(name:str):
    return {"message": f"Hello, {name}"}

@router.get("/health")
async def health_check():
    return {"status": "healthy"}