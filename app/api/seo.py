"""
SEO API endpoints
Provides sitemap and robots.txt generation
"""
from fastapi import APIRouter
from fastapi.responses import Response
from datetime import datetime
from ..core.database import get_content_collection, get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Depends

router = APIRouter(prefix="/seo", tags=["SEO"])


@router.get("/sitemap.xml")
async def generate_sitemap(db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Generate dynamic sitemap.xml with all articles
    """
    base_url = "https://.com"
    
    # Static pages
    urls = [
        f"  <url><loc>{base_url}/</loc><lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>",
        f"  <url><loc>{base_url}/about-us</loc><lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>",
        f"  <url><loc>{base_url}/income-tax</loc><lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>",
        f"  <url><loc>{base_url}/gst</loc><lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>",
        f"  <url><loc>{base_url}/mca</loc><lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>",
        f"  <url><loc>{base_url}/sebi</loc><lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>",
        f"  <url><loc>{base_url}/ms-office</loc><lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>",
    ]
    
    # Dynamic article URLs
    try:
        collection = await get_content_collection()
        cursor = collection.find({}).sort("date", -1)
        
        async for article in cursor:
            article_id = str(article.get("_id", ""))
            if article_id:
                lastmod = article.get("date", datetime.now())
                if isinstance(lastmod, datetime):
                    lastmod_str = lastmod.strftime('%Y-%m-%d')
                else:
                    lastmod_str = datetime.now().strftime('%Y-%m-%d')
                
                urls.append(
                    f"  <url><loc>{base_url}/article/{article_id}</loc><lastmod>{lastmod_str}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>"
                )
    except Exception as e:
        pass  # Continue even if articles can't be fetched
    
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    
    return Response(content=sitemap, media_type="application/xml")


@router.get("/robots.txt")
async def get_robots():
    """
    Generate robots.txt
    """
    robots_content = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
Disallow: /submit-article
Disallow: /login

Sitemap: https://.com/api/seo/sitemap.xml
"""
    return Response(content=robots_content, media_type="text/plain")
