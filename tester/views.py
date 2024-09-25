import threading
import time
import requests
from django.http import HttpResponse
from django.shortcuts import render
from requests.auth import HTTPBasicAuth

results = []


def send_request(url, auth=None, headers=None):
    try:
        if auth:
            response = requests.get(url, auth=auth)
        elif headers:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url)

        results.append({
            'status_code': response.status_code,
            'url': url,
            'response_time': response.elapsed.total_seconds(),
        })
        print(f"Status code: {response.status_code}")
        print(f"Url: {url}")
        print(f"Response time: {response.elapsed.total_seconds()}")
    except requests.exceptions.RequestException as e:
        print(f"Status code: None")
        print(f"Url: {url}")
        print(f"Error : {str(e)}")
        results.append({
            'status_code': None,
            'url': url,
            'error': str(e),
        })


def run_test_for_duration(duration, url, auth, headers, requests_per_sec, users_count):
    stop_time = time.time() + duration
    while time.time() < stop_time:
        threads = []
        for _ in range(users_count):
            thread = threading.Thread(target=send_request, args=(url, auth, headers))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        time.sleep(1)


def start_load_test(request):
    global results
    results = []

    if request.method == 'POST':
        url = request.POST.get('url')
        users_count = request.POST.get('users', None)
        requests_per_sec = request.POST.get('requests_per_sec', None)
        test_duration = request.POST.get('test_duration', None)
        auth_type = request.POST.get('auth_type')
        auth_data = request.POST.get('auth_data')

        if users_count is None or requests_per_sec is None or test_duration is None:
            return HttpResponse("Iltimos, barcha maydonlarni to'ldiring.")

        try:
            users_count = int(users_count)
            requests_per_sec = int(requests_per_sec)
            test_duration = int(test_duration)
        except ValueError:
            return HttpResponse("Foydalanuvchilar soni, so'rovlar soni va test davomiyligi raqam bo'lishi kerak.")

        auth = None
        headers = None

        if auth_type == 'basic' and ':' in auth_data:
            username, password = auth_data.split(':')
            auth = HTTPBasicAuth(username, password)
        elif auth_type == 'token':
            headers = {'Authorization': f'Bearer {auth_data}'}

        run_test_for_duration(test_duration, url, auth, headers, requests_per_sec, users_count)

        status_200 = len([res for res in results if res['status_code'] == 200])
        status_400 = len([res for res in results if res['status_code'] >= 400])
        long_time = 0
        for res in results:
            ttime = res['response_time']
            if ttime > long_time:
                long_time = ttime
            else: continue



        return render(request, 'results.html', {'results': results, 'status_200': status_200, 'status_400': status_400, 'long_time': long_time})

    return render(request, 'index.html')
