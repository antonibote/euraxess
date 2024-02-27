import argparse
import requests
from bs4 import BeautifulSoup
import json

def fetch_and_parse_url(url):
    print(f"Fetching URL: {url}")
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser') if response.status_code == 200 else None

def extract_job_info(job_url):
    soup = fetch_and_parse_url(job_url)
    if soup:
        job_info = {
            "JobTitle": soup.select_one('h1').text.strip() if soup.select_one('h1') else "N/A",
            "Organization": soup.select_one("dt:-soup-contains('Organisation/Company') + dd").text.strip() if soup.select_one("dt:-soup-contains('Organisation/Company') + dd") else "N/A",
            "ResearchField": soup.select_one("dt:-soup-contains('Research Field') + dd").text.strip() if soup.select_one("dt:-soup-contains('Research Field') + dd") else "N/A",
            "Profiles": soup.select_one("dt:-soup-contains('Researcher Profile') + dd").text.strip() if soup.select_one("dt:-soup-contains('Researcher Profile') + dd") else "N/A",
            "ApplicationDeadline": soup.select_one("dt:-soup-contains('Application Deadline') + dd").text.strip() if soup.select_one("dt:-soup-contains('Application Deadline') + dd") else "N/A",
            "JobStatus": soup.select_one("dt:-soup-contains('Job Status') + dd").text.strip() if soup.select_one("dt:-soup-contains('Job Status') + dd") else "N/A",
            "Location": soup.select_one("dt:-soup-contains('Country') + dd").text.strip() if soup.select_one("dt:-soup-contains('Country') + dd") else "N/A",
            "ContactDetails": {
                "Email": soup.select_one("dt:-soup-contains('E-mail') + dd").text.strip() if soup.select_one("dt:-soup-contains('E-mail') + dd") else "N/A",
                "Website": soup.select_one("dt:-soup-contains('Website') + dd a").get('href', '').strip() if soup.select_one("dt:-soup-contains('Website') + dd a") else "N/A"
            },
            "Funding": soup.select_one("dt:-soup-contains('Funding') + dd").text.strip() if soup.select_one("dt:-soup-contains('Funding') + dd") else "Not specified"
        }
        return job_info
    return {"Error": "Page not found or content not accessible"}

def extract_all_jobs(base_url, search_url):
    all_jobs = []
    current_url = search_url

    while current_url:
        soup = fetch_and_parse_url(current_url)
        if not soup: break

        job_links = soup.select('article > div > h1 > a') 
        for link in job_links:
            job_detail_url = f"{base_url.rstrip('/')}/{link['href'].lstrip('/')}"
            job_info = extract_job_info(job_detail_url)
            all_jobs.append(job_info)

        next_page_link = soup.select_one('.ecl-pagination__item--next a')
        if next_page_link:
            next_page_relative = next_page_link.get('href')
            current_url = f"{search_url}{next_page_relative}"
        else:
            break

    return all_jobs


def main():
    parser = argparse.ArgumentParser(description="Extract job offer information.")
    parser.add_argument("base_url", type=str, help="The base URL of the website.")
    parser.add_argument("search_url", type=str, help="The URL of the job listing page.")
    args = parser.parse_args()
    
    all_jobs = extract_all_jobs(args.base_url, args.search_url)
    print(json.dumps(all_jobs, indent=4))

if __name__ == "__main__":
    main()