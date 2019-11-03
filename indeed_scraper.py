import pprint
import time
import functools
import argparse
import os
import json
from collections import OrderedDict
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup


def timer(func):
    '''Print the runtime of the decorated function'''
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f'Finished scraping in {run_time:4f} secs')
        return result
    return wrapper_timer


def save_config(parsed_args):
    with open('scrape_cfg.json', 'w') as json_file:
        json.dump(parsed_args, json_file)


def load_config():
    with open('scrape_cfg.json') as json_file:
        options = json.load(json_file)
    return options


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('location', help='city, state, or zipcode')
    parser.add_argument(
        '-r', '--radius', help='radius from location', type=int)
    parser.add_argument('-s', '--salary', help='desired salary', type=int)
    parser.add_argument(
        '-j', '--job_type', help='fulltime, parttime, commission, temporary, contract, internship')
    parser.add_argument('-e', '--exp_lvl',
                        help='entry_level, mid_level, senior_level')
    parser.add_argument(
        '--sort', help='sort by date (most recent first)', action='store_true')
    args = parser.parse_args()

    args_dict = {
        'location': args.location,
        'radius': args.radius,
        'salary': args.salary,
        'job_type': args.job_type,
        'exp_level': args.exp_lvl,
        'sort_by_date': args.sort
    }

    return args_dict


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


def scrape_jobs(base_url, num_pages):
    # base_url = 'http://indeed.com/jobs?q=&l=Folsom%2C+CA'
    jobs_list = []

    for i in tqdm(range(num_pages)):
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


@timer
def main():
    args = parse_args()

    if os.path.isfile('scrape_cfg.json'):
        saved_args = load_config()
        saved_args.update({k: v for k, v in args.items() if v is not None})
        args = saved_args

    save_config(args)

    base_url = craft_base_url(**args)
    search_term = input("Search term: ")
    jobs = scrape_jobs(base_url, int(input("Number of pages to scrape: ")))

    job_results = []

    for job in jobs:
        if search_term.lower() in job['Title'].lower() or search_term.lower() in job['Summary'].lower():
            job_results.append(job)

    if job_results:
        print(
            f"Returning {len(job_results)} jobs containing '{search_term}'...\n")
        for job in job_results:
            print(str(job), end='\n\n')
    else:
        print(f"No jobs found containing '{search_term}'.")


if __name__ == '__main__':
    main()
