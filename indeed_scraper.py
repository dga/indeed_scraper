import pprint
from collections import OrderedDict
import requests
from bs4 import BeautifulSoup


def craft_base_url(location=None, radius=None, salary=None, job_type=None, exp_level=None, sort_by_date=None):
    url = f'https://www.indeed.com/'

    if location:
        url += 'jobs?q='
        if salary:
            url += f'${salary}'
        if location:
            url += f'&l={location}'
        if radius:
            url += f'&radius={str(radius)}'
        if job_type:
            url += f'&jt={job_type}'
        if exp_level:
            url += f'&explvl={exp_level}'
        if sort_by_date:
            url += '&sort=date'
    else:
        url += '?sq = 1'

    return url


def scrape_jobs(num_pages):
    base_url = 'http://indeed.com/jobs?q=&l=Folsom%2C+CA'
    jobs_list = []

    for i in range(num_pages):
        modified_url = base_url + f'&start={i * 10}'
        res = requests.get(modified_url)
        soup = BeautifulSoup(res.text, 'lxml')

        jobs = soup(class_='jobsearch-SerpJobCard')

        for item in jobs:
            job_title = item.find(class_='title')

            if job_title.text:
                job_title = job_title.text.strip()

            summary = item.find(class_='summary')

            if summary.text:
                summary = summary.text.strip()

            company = item.find(class_='company')

            if company.text:
                company = company.text.strip()

            salary = item.find(class_='salaryText')

            if salary:
                salary = salary.text.strip()

            url = f"https://www.indeed.com{item.find('a').get('href')}"

            jobs_list.append(OrderedDict([('Title', job_title), ('Summary', summary),
                                          ('Company', company), ('Salary', salary), ('URL', url)]))

    return jobs_list


def main():
    jobs = scrape_jobs(int(input("How many pages? ")))
    search_term = input("Search term: ")

    job_results = []

    for job in jobs:
        if search_term.lower() in job['Title'].lower() or search_term.lower() in job['Summary'].lower():
            job_results.append(job)

    if job_results:
        print(
            f"Returning {len(job_results)} jobs containing '{search_term}'...\n")
        for job in job_results:
            print(str(job))
    else:
        print(f"No jobs found containing '{search_term}'.")


if __name__ == '__main__':
    print(craft_base_url("folsom", 10, 20000, "fulltime", "senior_level", True))

   # location = None, radius = None, salary = None, job_type = None, exp_level = None, sort_by_date = None):
