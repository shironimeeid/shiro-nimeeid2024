import tools
from bs4 import BeautifulSoup

baseURL = "https://h.mangabat.com/mangabat/"
altURL = "https://readmangabat.com/mangabat/"

def index(request):
    response = tools.get(baseURL)
    return { 'success': True, 'statusCode': response.status_code }

def home(request):
    response = tools.get(baseURL)
    data = response.text
    soup = BeautifulSoup(data, "html.parser")
    main = soup.find(class_="body-site")
    
    obj = {
        "title": "Home",
        "url": request.build_absolute_uri(),
        "popular": [],
        "latest": []
    }
    
    # Populate popular mangas
    popular = main.find(id="owl-slider").find_all(class_="item")
    for manga in popular:
        name = manga.find("a").text
        thumb = manga.find("img").get("src")
        url = manga.find("a").get("href")
        endpoint = url.replace(baseURL, "").replace(altURL, "")
        
        chapter_name = manga.find_all("a")[1].text
        chapter_url = manga.find_all("a")[1].get("href")
        chapter_endpoint = chapter_url.replace(baseURL, "").replace(altURL, "")
        
        obj["popular"].append({
            'name': name,
            'thumb': thumb,
            'url': url,
            'endpoint': endpoint,
            'chapter': {
                'name': chapter_name,
                'url': chapter_url,
                'endpoint': chapter_endpoint
            }
        })
    
    # Populate latest mangas
    latest = main.find_all(class_="content-homepage-item")
    for manga in latest:
        name = manga.find(class_="item-img").get("title")
        thumb = manga.find("img").get("src")
        score = manga.find(class_="item-rate").text
        url = manga.find(class_="item-img").get("href")
        endpoint = url.replace(baseURL, "").replace(altURL, "")
        
        arr_chapter = []
        chapters = manga.find_all(class_="item-chapter")
        for chapter in chapters:
            chapter_name = chapter.find("a").text
            chapter_url = chapter.find("a").get("href")
            chapter_endpoint = chapter_url.replace(baseURL, "").replace(altURL, "")
            arr_chapter.append({ 'name': chapter_name, 'url': chapter_url, 'endpoint': chapter_endpoint })
        
        obj["latest"].append({
            'name': name,
            'thumb': thumb,
            'url': url,
            'endpoint': endpoint,
            'score': '⭐' + score,
            'chapters': arr_chapter
        })
    
    return obj

def comic(request, endpoint):
    # Assuming baseURL and altURL are defined somewhere in your settings or constants
    baseURL = "https://h.mangabat.com"
    altURL = "https://alt.mangabat.com"

    try:
        # Attempt to fetch data from the primary URL
        response = requests.get(f"{baseURL}{endpoint}")
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Check if the page indicates a 404 error
        is404 = soup.find(style="font: 700 22px sans-serif;")
        if is404 and "404" in is404.text:
            # If 404, attempt to fetch data from alternative URL
            response = requests.get(f"{altURL}/read/{endpoint}")
            soup = BeautifulSoup(response.text.replace(altURL, baseURL), "html.parser")
            is404 = soup.find(style="font: 700 22px sans-serif;")
            
            if is404 and "404" in is404.text:
                # If still 404, return failure response
                return JsonResponse({ 'success': False, 'statusCode': 404 })
        
        # Initialize an object to store comic information
        obj = {
            "name": soup.find(class_="story-info-right").find("h1").text,
            "thumb": soup.find(class_="info-image").find("img").get("src"),
            "alter": soup.find(class_="variations-tableInfo").find_all("tr")[0].find(class_="table-value").text,
            "authors": [],
            "status": soup.find(class_="variations-tableInfo").find_all("tr")[2].find(class_="table-value").text,
            "genres": [],
            "synopsis": soup.find(class_="panel-story-info-description").text.strip(),
            "chapters": []
        }
        
        # Populate authors
        authors = soup.find(class_="variations-tableInfo").find_all("tr")[1].find(class_="table-value").find_all("a")
        for author in authors:
            author_name = author.text
            author_url = author.get("href")
            author_endpoint = author_url.replace(baseURL, "")
            obj["authors"].append({ 'name': author_name, 'url': author_url, 'endpoint': author_endpoint })
        
        # Populate genres
        genres = soup.find(class_="variations-tableInfo").find_all("tr")[3].find(class_="table-value").find_all("a")
        for genre in genres:
            genre_name = genre.text
            genre_url = genre.get("href")
            genre_endpoint = genre_url.replace(baseURL, "")
            obj["genres"].append({ 'name': genre_name, 'url': genre_url, 'endpoint': genre_endpoint })
        
        # Populate extended info
        info_extends = soup.find(class_="story-info-right-extent").find_all("p")
        for info in info_extends:
            key = info.find(class_="stre-label").text.split(":")[0].lower().strip().replace(" ", "_")
            value = info.find(class_="stre-value").text
            obj[key] = value
        
        # Populate chapters
        chapters = soup.find(class_="row-content-chapter").find_all("li")
        for chapter in chapters:
            name = chapter.find("a").text
            date = chapter.find(class_="chapter-time text-nowrap").text
            url = chapter.find("a").get("href")
            endpoint = url.replace(baseURL, "").replace(altURL, "")
            obj["chapters"].append({ 'name': name, 'date': date, 'url': url, 'endpoint': endpoint })
        
        return JsonResponse(obj)
    
    except Exception as e:
        # Handle any exceptions that might occur during the fetching or parsing
        return JsonResponse({ 'success': False, 'error': str(e) })

def chapter(request, endpoint):
    response = tools.get(f"{baseURL}{endpoint}")
    soup = BeautifulSoup(response.text, "html.parser")
    
    is404 = soup.find(style="font: 700 22px sans-serif;")
    if is404 and "404" in is404.text:
        response = tools.get(f"https://h.mangabat.com/mangabat/{endpoint}")
        soup = BeautifulSoup(response.text, "html.parser")
        is404 = soup.find(style="font: 700 22px sans-serif;")
        
        if is404 and "404" in is404.text:
            return { 'success': False, 'statusCode': 404 }
    
    obj = {
        "title": soup.find(class_="panel-chapter-info-top").find("h1").text.capitalize(),
        "thumb": soup.find("meta", property="og:image").get("content"),
        "synopsis": soup.find("meta", property="og:description").get("content"),
        "chapters": []
    }
    
    # Populate chapter images
    chapters = soup.find(class_="container-chapter-reader").find_all("img")
    for chapter in chapters:
        image = chapter.get("src").replace("https://", "")
        uri = f"https://cdn-mangabat.katowproject.workers.dev/{image}"
        obj["chapters"].append(uri)
    
    # Populate previous and next chapter endpoints
    chapter_prev = soup.find(class_="navi-change-chapter-btn-prev")
    chapter_next = soup.find(class_="navi-change-chapter-btn-next")
    
    if chapter_prev:
        obj["chapter"]["prev"] = chapter_prev.get("href").replace(baseURL, "").replace(altURL, "")
    else:
        obj["chapter"]["prev"] = None
    
    if chapter_next:
        obj["chapter"]["next"] = chapter_next.get("href").replace(baseURL, "").replace(altURL, "")
    else:
        obj["chapter"]["next"] = None
    
    return obj

def search(request, query):
    page = request.GET.get("page", 1)
    query = query.replace(" ", "_")
    response = tools.get(f"{baseURL}/search/manga/{query}/?page={page}")
    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find(class_="body-site")
    
    obj = {
        "mangas": [],
        "pagination": []
    }
    
    # Populate search results
    mangas = main.find(class_="panel-list-story").find_all(class_="list-story-item")
    for manga in mangas:
        name = manga.find("a").get("title")
        thumb = manga.find("img").get("src")
        url = manga.find("a").get("href")
        endpoint = url.replace(baseURL, "").replace(altURL, "")
        obj["mangas"].append({ 'name': name, 'thumb': thumb, 'url': url, 'endpoint': endpoint })
    
    # Populate pagination
    pagination = main.find(class_="panel-page-number").find_all("a")
    for page in pagination:
        name = page.text
        if "FIRST" in name:
            name = "<< First Page"
        elif "LAST" in name:
            name = "Last Page >>"
        url = page.get("href", None)
        
        endpoint = url
        if url:
            endpoint = url.replace(baseURL, "").replace(altURL, "").replace("comic/manga", "")
        
        obj["pagination"].append({ 'name': name, 'url': url, 'endpoint': endpoint })
    
    return obj

def genre(request, query):
    response = tools.get(f"{baseURL}/genre/{query}")
    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find(class_="body-site")
    
    obj = {
        "mangas": [],
        "pagination": []
    }
    
    # Populate genre results
    mangas = main.find(class_="panel-list-story").find_all(class_="list-story-item")
    for manga in mangas:
        name = manga.find("a").get("title")
        thumb = manga.find("img").get("src")
        url = manga.find("a").get("href")
        endpoint = url.replace(baseURL, "").replace(altURL, "")
        obj["mangas"].append({ 'name': name, 'thumb': thumb, 'url': url, 'endpoint': endpoint })
    
    # Populate pagination
    pagination = main.find(class_="panel-page-number").find_all("a")
    for page in pagination:
        name = page.text
        if "FIRST" in name:
            name = "<< First Page"
        elif "LAST" in name:
            name = "Last Page >>"
        url = page.get("href", None)
        
        endpoint = url
        if url:
            endpoint = url.replace(baseURL, "").replace(altURL, "").replace("comic/manga", "")
        
        obj["pagination"].append({ 'name': name, 'url': url, 'endpoint': endpoint })
    
    return obj

def manga(request, query):
    response = tools.get(f"{baseURL}/manga/{query}")
    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find(class_="body-site")
    
    obj = {
        "mangas": [],
        "pagination": []
    }
    
    # Populate genre results
    mangas = main.find(class_="panel-list-story").find_all(class_="list-story-item")
    for manga in mangas:
        name = manga.find("a").get("title")
        thumb = manga.find("img").get("src")
        url = manga.find("a").get("href")
        endpoint = url.replace(baseURL, "").replace(altURL, "")
        obj["mangas"].append({ 'name': name, 'thumb': thumb, 'url': url, 'endpoint': endpoint })
    
    # Populate pagination
    pagination = main.find(class_="panel-page-number").find_all("a")
    for page in pagination:
        name = page.text
        if "FIRST" in name:
            name = "<< First Page"
        elif "LAST" in name:
            name = "Last Page >>"
        url = page.get("href", None)
        
        endpoint = url
        if url:
            endpoint = url.replace(baseURL, "").replace(altURL, "").replace("comic/manga", "")
        
        obj["pagination"].append({ 'name': name, 'url': url, 'endpoint': endpoint })
    
    return obj

def alur(request):
    response = tools.get(f"{baseURL}/alur/")
    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find(class_="body-site")
    
    obj = {
        "mangas": [],
        "pagination": []
    }
    
    # Populate genre results
    mangas = main.find(class_="panel-list-story").find_all(class_="list-story-item")
    for manga in mangas:
        name = manga.find("a").get("title")
        thumb = manga.find("img").get("src")
        url = manga.find("a").get("href")
        endpoint = url.replace(baseURL, "").replace(altURL, "")
        obj["mangas"].append({ 'name': name, 'thumb': thumb, 'url': url, 'endpoint': endpoint })
    
    # Populate pagination
    pagination = main.find(class_="panel-page-number").find_all("a")
    for page in pagination:
        name = page.text
        if "FIRST" in name:
            name = "<< First Page"
        elif "LAST" in name:
            name = "Last Page >>"
        url = page.get("href", None)
        
        endpoint = url
        if url:
            endpoint = url.replace(baseURL, "").replace(altURL, "").replace("comic/manga", "")
        
        obj["pagination"].append({ 'name': name, 'url': url, 'endpoint': endpoint })
    
    return obj

def subchapter(request, query):
    response = tools.get(f"{baseURL}/subchapter/{query}")
    soup = BeautifulSoup(response.text, "html.parser")
    main = soup.find(class_="body-site")
    
    obj = {
        "mangas": [],
        "pagination": []
    }
    
    # Populate genre results
    mangas = main.find(class_="panel-list-story").find_all(class_="list-story-item")
    for manga in mangas:
        name = manga.find("a").get("title")
        thumb = manga.find("img").get("src")
        url = manga.find("a").get("href")
        endpoint = url.replace(baseURL, "").replace(altURL, "")
        obj["mangas"].append({ 'name': name, 'thumb': thumb, 'url': url, 'endpoint': endpoint })
    
    # Populate pagination
    pagination = main.find(class_="panel-page-number").find_all("a")
    for page in pagination:
        name = page.text
        if "FIRST" in name:
            name = "<< First Page"
        elif "LAST" in name:
            name = "Last Page >>"
        url = page.get("href", None)
        
        endpoint = url
        if url:
            endpoint = url.replace(baseURL, "").replace(altURL, "").replace("comic/manga", "")
        
        obj["pagination"].append({ 'name': name, 'url': url, 'endpoint': endpoint })
    
    return obj
