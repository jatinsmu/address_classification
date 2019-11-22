import json
import pickle
import re
import sys
from collections import Counter

import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask import request, jsonify
from google_images_download import google_images_download

app = Flask(__name__)
USER_AGENT = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
api_key = ""  # Enter your google api key here
loaded_model = pickle.load(open('model.pkl', 'rb'))
model_threshold = 0.7


def get_map_image(address):
    url = "https://maps.googleapis.com/maps/api/staticmap?"
    center = address
    zoom = 17
    format = "png"
    size = "200x200"
    map_type = "hybrid"
    link = url + "center=" + center + "&zoom=" + str(
        zoom) + "&size=" + size + "&key=" + api_key + "&sensor= false&format=" + format + "&maptype=" + map_type
    return link


def get_street_view(address):
    url = "https://maps.googleapis.com/maps/api/streetview?"
    location = address
    size = "200x200"
    fov = 120
    link = url + "location=" + location + "&size=" + size + "&key=" + api_key + "&fov=" + str(fov)
    return link


# returns string address
def get_formatted_address(input):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    r = requests.get(url + "?address=" + input + "&key=" + api_key)
    response = json.loads(r.content.decode())
    address = response['results'][0]['formatted_address']
    return address


# return type list
def get_images(address):
    orig_stdout = sys.stdout
    f = open('URLS.txt', 'w')
    sys.stdout = f
    response = google_images_download.googleimagesdownload()
    arguments = {"keywords": address, "limit": 1, "print_urls": True}
    paths = response.download(arguments)
    sys.stdout = orig_stdout
    f.close()

    with open('URLS.txt') as f:
        content = f.readlines()
    f.close()
    urls = []
    for j in range(len(content)):
        if content[j][:9] == 'Completed':
            urls.append(content[j - 1][11:-1])
    return urls


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(number_results, int), 'Number of results must be an integer'
    escaped_search_term = search_term.replace(' ', '+')

    google_url = 'http://www.google.co.in/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results,
                                                                           language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()
    return search_term, response.text


def parse_results(html, keyword):
    soup = BeautifulSoup(html, 'html.parser')
    found_results = []
    rank = 1
    result_block = soup.find_all('div', attrs={'class': 'g'})
    for result in result_block:
        link = result.find('a', href=True)
        title = result.find('h3')
        description = result.find('span', attrs={'class': 'st'})
        if link and title:
            link = link['href']
            title = title.get_text()
            if description:
                description = description.get_text()
            if link != '#':
                found_results.append({'description': description})

                rank += 1
    return (found_results)


def get_result(address):
    keyword, html = fetch_results(address, 15, 'en')
    string = parse_results(html, keyword)
    split_add = address.replace(",", " ").split(" ")
    split_add = [x.lower() for x in split_add]
    se = []
    for i in range(len(string)):
        se.append(string[i]['description'])
    str1 = ''.join(se)
    tok = str1.split(" ")
    tok = [x.lower() for x in tok]

    files_cleaned = [re.sub(r"[-()\"#/&@;:<>{}`+=~|.!?,]", "", file) for file in tok]
    files_cleaned1 = [''.join(x for x in i if x.isalpha()) for i in files_cleaned]
    add_list = [x for x in files_cleaned1 if x not in split_add]
    stop_words = [
        'nova', 'scotia', 'address', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
        "you've", "you'll", "you'd", 'your',
        'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself',
        'it', "it's", 'its', 'itself',
        'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll",
        'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
        'until', 'while',
        'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
        'above', 'below',
        'to', 'from', 'halifax', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
        'once', 'here', 'there', 'when', 'where',
        'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'address', 'well', 'costs',
        'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll',
        'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't",
        'hadn', "hadn't",
        'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn',
        "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'street',
        'wasn', "wasn't", 'weren', "weren't", 'hours', 'opening', 'closing''won', 'canada', "won't", 'wouldn',
        "wouldn't", 'find', 'north', 'south', 'reviews', 'view', 'information', 'road', 'directions', 'phone', 'number',
        'location', 'email'
    ]
    a1 = [word for word in add_list if word not in stop_words]
    files_cleaned2 = [w for w in a1 if len(w) > 3]
    str_list = list(filter(None, files_cleaned2))
    counts = dict(Counter(str_list))
    your_dic = {k: v for k, v in counts.items() if v != (1)}
    newA = sorted(your_dic, key=your_dic.get, reverse=True)[:5]
    lib = {
        'Residential': ['condo', 'apartment', 'property', 'bedroom', 'room', 'apt', 'bungalow', 'cabin', 'apartments',
                        'house', 'home', 'condominium', 'farmhouse', 'apartment', 'dwelling', 'flat', 'townhouse',
                        'home', 'community', 'homestead', 'housing', 'residency'],
        'Non Residential': ['elementary', 'middle', 'school', 'high school', 'college', 'university', 'preschool',
                            'daycare', 'training center', 'education', 'grocery', 'store', 'shop',
                            'market', 'gas station', 'store', 'restaurant', 'cafeteria', 'catering', 'bar', 'hospital',
                            'rehabilitation', 'motel', 'dormitory', 'fraternity'
            , 'monastery', 'showroom', 'office', 'bank', 'community', 'center', 'cinema', 'theater', 'casino',
                            'library', 'armory', 'police station', 'fire station',
                            'jail', 'reformatory ', 'penitentiary', 'vehicle service', 'refrigerated warehouse',
                            'airplane hangar', 'laboratory', 'telephone switching', 'crematorium',
                            'telephone switching', 'copy center', 'printing shop', 'tanning salon', 'probation office',
                            'enclosed mall', 'university', 'reception hall', 'supercentre', 'museum', 'repair shop',
                            'data center', 'enclosed mall', 'salon', 'mall', 'pool', 'swimming pool',
                            'veterinary_care', 'jewelry_store', 'hair_care', 'gym', 'airport', 'amusement_park',
                            'aquarium', 'aquarium', 'atm', 'bakery', 'liquor_store', 'lodging', 'night_club', 'rv_park',
                            'supermarket', 'roofing_contractor', 'pet_store',
                            'parking', 'park', 'moving_company', 'post_office', 'supermarket', 'taxi_stand', 'plumber',
                            'physiotherapist', 'car_dealer', 'bowling_alley', 'book_store', 'bicycle_store',
                            'beauty_salon', 'art_gallery',
                            'car_dealer', 'car_wash', 'courthouse', 'hardware', 'store', 'subway', 'station', 'embassy',
                            'drugstore', 'doctor', 'train', 'station', 'transit', 'station', 'travel', 'agency', 'pet',
                            'store', 'night', 'club',
                            'shoe', 'spa', 'cemetery', 'furniture', 'temple', 'hindu', 'electronics', 'dentist']}
    resident_keywords = 0
    non_resident_keywords = 0
    resident_types = []
    non_resident_types = []
    other_types = []

    for word in newA:
        if word in lib['Residential']:
            resident_keywords += 1
            resident_types.append(word)

        elif word in lib['Non Residential']:

            non_resident_keywords += 1
            non_resident_types.append(word)
        else:
            other_types.append(word)

    if resident_keywords > non_resident_keywords:
        result = "Residential"
        return result, resident_types
    elif non_resident_keywords > resident_keywords:
        result = "Non Residential"
        return result, non_resident_types
    else:
        result = "Other"
        return result, other_types


def get_model_result(street_number, street_name, street_type, postal_code):
    street_number = int(street_number)
    new_df = pd.DataFrame({"postal_code": [postal_code], "street_number": [street_number], "street_name": [street_name],
                           'street_type': [street_type]})
    tfidfconverter = loaded_model._vectorizer  # keeping the same vectorizer as in model
    # new_df['street_number'] = tfidfconverter.transform(new_df['street_number']).toarray()
    new_df['street_name'] = tfidfconverter.transform(new_df['street_name']).toarray()
    new_df['street_type'] = tfidfconverter.transform(new_df['street_type']).toarray()
    new_df['postal_code'] = tfidfconverter.transform(new_df['postal_code']).toarray()
    result = str(loaded_model.predict(new_df)[0])
    prob = list(loaded_model.predict_proba(new_df)[0])
    if result == "Residential":
        score = prob[1]

    else:
        score = prob[0]

    return result, score


@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    response = request.json
    input = response['queryResult']['parameters']['address']
    address = get_formatted_address(input)
    web_address = address
    print(address)
    address = address.replace(', Canada', '')
    address_list = address.split(',')

    street_number = address_list[0].split(' ')[0]
    street_type = address_list[0].split(' ')[-1]
    street_name_list = address_list[0].split(' ')
    street_name_list.remove(street_number)
    street_name_list.remove(street_type)
    street_name = " ".join(street_name_list)
    temp = address_list[-1].split(' ')
    postal_code = temp[-2] + temp[-1]
    model_result, score = get_model_result(street_number, street_name, street_type, postal_code)
    print("Model result: ", model_result)
    print("score: ", score)
    web_result, types = get_result(web_address)
    print("web result: ", web_result)
    map = get_map_image(web_address)
    street_view = get_street_view(web_address)

    result = {}

    if model_result != web_result:
        if score > model_threshold:
            final_result = "Mixed Residential and Non Residential"
            result['fulfillmentText'] = final_result + "[" + ",".join(types) + "]"
        else:
            final_result = web_result
            result['fulfillmentText'] = final_result + "[" + ",".join(types) + "]"
    else:
        final_result = web_result
        result['fulfillmentText'] = final_result + "[" + ",".join(types) + "]"

    result['fulfillmentMessages'] = [
        {
            "card": {
                "title": result['fulfillmentText'],
                "imageUri": map
            }
        },
        {
            "card": {
                "title": result['fulfillmentText'],
                "imageUri": street_view
            }
        }
    ]
    print(json.dumps(result))
    return jsonify(result)


# run the app
if __name__ == '__main__':
    app.run(debug=True, port=80)
