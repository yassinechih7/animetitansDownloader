from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import requests, os

# ****************************************************************************
# *                           google Drive download                          *
# ****************************************************************************

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def downladListOfGdriveUrls(eplink):
	print(eplink)
	parsed_url = urlparse(eplink[1])
	id = parse_qs(parsed_url.query)['id'][0]
	download_file_from_google_drive(id, eplink[0]+'.mp4')

# ****************************************************************************
# *                              safely get html                             *
# ****************************************************************************

def getTheSoup(url):
	try:
	    r = requests.get(url,timeout=3)
	    html_doc = r.text
	except requests.exceptions.HTTPError as errh:
	    print ("Http Error:",errh)
	except requests.exceptions.ConnectionError as errc:
	    print ("Error Connecting:",errc)
	except requests.exceptions.Timeout as errt:
	    print ("Timeout Error:",errt)
	except requests.exceptions.RequestException as err:
	    print ("OOps: Something Else",err)

	soup = BeautifulSoup(html_doc, 'lxml')
	return soup


# ****************************************************************************
# *                            getDownloadLink                            *
# ****************************************************************************
def decodeEpName(title):

	decodedString = title.encode("iso-8859-1").decode('utf-8')
	return decodedString


def getDownloadLink(url):
	soup = getTheSoup(url)
	selector = 'div.entry-content > div.bixbox.mctn > div > ul > li:not(li.head)'
	DowloadLinkList = soup.select(selector)
	epTitle = decodeEpName(soup.find(class_='entry-title').getText())


	for i in DowloadLinkList:
		if i.select('b')[0].text == ' GoogleDrive':
			return [epTitle, (i.find('a')['href']).replace('<br /> ', '')]

	


# ****************************************************************************
# *                              Get ep url list                             *
# ****************************************************************************

def getEpList(url):
	# #post-23 > div.bixbox.bxcl.epcheck > div.eplister > ul
	soup = getTheSoup(url)
	allEpListCode = soup.select('div.bixbox.bxcl.epcheck>div.eplister>ul')[0]
	epList = [ x ['href'] for x in allEpListCode.find_all('a')]
	return epList



animeUrl = u'https://animetitans.com/anime/ousama-ranking/'




# ****************************************************************************
# *                              Download all ep                             *
# ****************************************************************************

def downloadAllEp():
	allEpList = getEpList(animeUrl)
	allEp = [ getDownloadLink(ep) for ep in allEpList ]

	for ep in allEp:
		downladListOfGdriveUrls(ep)


if __name__ == '__main__':
    animeUrl = input('Please insert anime url:\n>>> ')
    downloadAllEp()


