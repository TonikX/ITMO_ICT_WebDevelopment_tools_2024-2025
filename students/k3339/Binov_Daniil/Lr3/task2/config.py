SITES = [
    "https://www.lifehack.org/articles/productivity/10-time-management-tips-that-work.html",
    "https://www.forbes.com/advisor/business/time-management-tips/",
    "https://todoist.com/productivity-methods/time-management",
    "https://www.mindtools.com/pages/main/newMN_HTE.htm"
]
TOTAL_SITES = len(SITES)
CHUNK_SIZE = 2  
CHUNKS = TOTAL_SITES // CHUNK_SIZE + (1 if TOTAL_SITES % CHUNK_SIZE else 0)