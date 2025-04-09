from fastapi.responses import FileResponse
from stub.main import app

@app.get("/")
async def root():
    """Serve main page"""
    return FileResponse("page/index.html")

@app.get("/wordcloud")
async def word_cloud():
    """Serve word cloud page"""
    return FileResponse("page/wordcloud.html")

@app.get("/messagelengths")
async def message_length():
    """Serve word message length chart page"""
    return FileResponse("page/message_length.html")

@app.get("/faq")
async def phrases():
    """Serve faq page"""
    return FileResponse("page/faq.html")

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    return FileResponse("assets/favicon.ico")
