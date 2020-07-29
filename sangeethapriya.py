from selenium import webdriver
import time
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import shutil
import os.path
from os import path
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException

email = "johnmcparty2020@gmail.com"
password = "Sangeetha"

artist_list = ["Mysore M Nagaraj,M Manjunath"]


class Downloadbot:
    def __init__(self, username, password):
        self.driver = webdriver.Chrome()
        self.driver.get("https://sangeethapriya.org")
        sleep(0.5)
        self.driver.find_element_by_xpath("//a[contains(@href,'http://www.sangeethapriya.org/search.php')]").click()
        sleep(0.5)
        self.driver.find_element_by_xpath('//form[@action="list_albums.php"]').click()
        self.driver.find_element_by_xpath('//option[@value="Carnatic"]').click()
        self.driver.find_element_by_xpath('//input[@value="FILTER"]').click()
        sleep(1)
        self.driver.find_element_by_xpath(
            "//a[contains(@href,'https://sangeethamshare.org/sreekanth/369-Sanjay_Subrahmanyan-Live_Concert52/')]").click()
        sleep(2)
        self.driver.find_element_by_xpath(
            '//img[@src="http://www.sangeethapriya.org/new-template/images/google.jpg"]').click()
        print("Sign in and click continue")
        print("Username: {}").format(username)
        print("Password: {}").format(password)
        sleep(1)
        signin_window = self.driver.window_handles[1]
        self.driver.switch_to_window(signin_window)
        self.driver.find_element_by_xpath('//input[@type="email"]').send_keys(username)
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/div").click()
        sleep(1.5)
        self.driver.find_element_by_xpath(
            '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input').send_keys(
            password)
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/div").click()
        sleep(2)
        main_window = self.driver.window_handles[0]
        self.driver.switch_to_window(main_window)
        self.driver.find_element_by_xpath("//a[contains(@href,'http://www.sangeethapriya.org/search.php')]").click()
        sleep(1)

    def handle_alert(self):
        is_alert = False
        try:
            alert_text = self.driver.switch_to.alert.text
            is_alert = True
        except NoAlertPresentException:
            is_alert = False
        return is_alert

    def handle_login(self):
        is_login = False
        if self.driver.find_element_by_xpath('//img[@src="http://www.sangeethapriya.org/new-template/images/google'
                                             '.jpg"]'):
            is_login = True
        return is_login

    def download_concerts(self, link):
        song_order = 0
        song_list = []
        read_me = ""
        is_empty = False
        self.driver.get(link)
        is_login_and_alert = False
        try:
            if self.driver.find_element_by_xpath('//img[@src="http://www.sangeethapriya.org/new-template/images/google.jpg"]'):
                sleep(15)
                self.driver.find_element_by_link_text("Click here to continue...").click()
        except UnexpectedAlertPresentException:
            is_empty = True
            is_login_and_alert = True
        except NoSuchElementException:
            is_empty = False

        # if login page randomly shows up, want to handle that (try)
        # if login and alert also shows up, skip over that (UnexpectedAlertPresent)
        # if login page does not show up, it is not empty (NoSuchElement)
        # if UnexpectedAlertPresent is triggered, SangeethaPriya moves onto a different page

        if not is_login_and_alert:
            try:
                alert_text = self.driver.switch_to.alert.text
                is_empty = True
            except NoAlertPresentException:
                is_empty = False

        # if only alert shows up,

        if not is_empty:
            all_links = self.driver.find_elements_by_xpath("//a[@class='download']")
            for link in all_links:
                file_type = link.find_element_by_xpath('..').text
                if 'MP3' in file_type:
                    print("downloading file")
                    link.click()
                    self.driver.find_element_by_class_name("main").click()
                    # song_list.append(str(self.driver.find_elements_by_tag_name('h2')[song_order].text))
                    song_order = song_order + 1
                    sleep(1)

            all_h1 = self.driver.find_elements_by_tag_name('h1')
            h1_texts = []
            for h1 in all_h1:
                h1_texts.append(h1.text)

            if 'Upload Notes' in h1_texts:
                html = self.driver.page_source
                read_me = extract_readme(html)

        return is_empty, song_list, read_me

    def get_concert_list_html(self, artist_name):
        self.driver.find_element_by_xpath("/html/body/div[4]/div/div[1]/form[4]/table/tbody/tr/td[2]/select").click()
        self.driver.find_element_by_xpath('//option[@value="{}"]'.format(artist_name)).click()
        self.driver.find_element_by_xpath("/html/body/div[4]/div/div[1]/form[4]/table/tbody/tr/td[3]/input").click()
        table = self.driver.find_element_by_xpath('//div[@id="searchresults"]').get_attribute('innerHTML')
        return table


def get_concert_links(html):
    concerts = []
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find("table", border=1).find("tbody").find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        individual_concert_entry = []
        if len(cells) != 0:
            individual_concert_entry.extend([str(cells[0].get_text()), str(cells[0].contents[0].attrs['href']),
                                             str(cells[1].get_text()), str(cells[2].get_text())])
            concerts.append(individual_concert_entry)
    concert_array = np.array(concerts)
    return concert_array


def create_concert_database_entry(song_list, artist, artist_listed, genre, concert_id, file_location):
    concert_entry = []
    for song in song_list:
        song_entry = []
        song_entry.extend([str(song), str(artist), str(artist_listed), '', '', '', '', str(genre), str(concert_id), '',
                           '', '', '', '', '', '', '', '', '', '', '', '', '', str(file_location), 'SangeethaPriya'])
        concert_entry.append(song_entry)
    database_entry = pd.DataFrame(concert_entry,
                                  columns=['song_name', 'main_artist', 'artist_listed', 'other_artist_1', 'other_artist_2',
                                           'other_artist_3', 'other_artist_4', 'genre', 'concert_id',  'song_order',
                                           'song_type', 'song_ragam', 'song_talam', 'composer', 'kalpana_swaram',
                                           'neraval', 'violin_accompaniment', 'mridangam_accompaniment_1',
                                           'mridangam_accompaniment_2', 'ghatam_accompaniment', 'kanjira_accompaniment',
                                           'morsing_accompaniment', 'tabla_accompaniment', 'file_location', 'source'])
    return database_entry


def create_artist_directory(artist):
    artist_path = '/Users/arjunneervannan/Desktop/SangeethaPriya/' + artist
    os.mkdir(artist_path)
    return artist_path


def create_concert_directory(artist, concert_id):
    concert_path = '/Users/arjunneervannan/Desktop/SangeethaPriya/' + artist + '/' + concert_id
    os.mkdir(concert_path)
    return concert_path


def get_recently_downloaded():
    song_list = []
    for file in os.listdir('/Users/arjunneervannan/Downloads/'):
        if file.endswith(".mp3"):
            song_list.append(file)
        elif file.endswith(".MP3"):
            song_list.append(file)
    return song_list


def move_song_files(song_filename, newpath):
    oldpath = '/Users/arjunneervannan/Downloads/' + song_filename
    newpath = newpath + '/' + song_filename + '.mp3'
    shutil.move(oldpath, newpath)
    print ("{song} moved!").format(song=song_filename)


def write_readme(readme_text, newpath, concert_id):
    filename = "README_" + concert_id + ".txt"
    completeName = os.path.join(newpath, filename)
    f = open(completeName, "w")
    f.write(readme_text)
    f.close()


def extract_readme(html):
    soup = BeautifulSoup(html, features="html.parser")

    y = soup.find(id='main')
    readme = False
    readme_text = ""
    for a in y.childGenerator():
        if (str(a) == '<h1>Upload Notes</h1>'):
            readme = True

        if (str(a) == '<a name="commentbox"></a>'):
            readme = False

        if readme:
            readme_text = readme_text + str(a)

    # cleantext = BeautifulSoup(readme_text, "lxml").text
    return readme_text


def time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  print("Time Lapsed = {0}:{1}:{2}".format(int(hours),int(mins),sec))


bot = Downloadbot(email, password)
# log into Sangeethapriya
num_concerts = 0
# bot.download_concerts("https://www.sangeethamshare.org/manjunath/Carnatic/Audio/UPLOADS-301-600/504-lAlgudi_G_jayarAman-n_ramaNi-duet-USA_2-70s/")
# bot.download_concerts("https://www.sangeethamshare.org/tvg/UPLOADS-3801---4000/3969-Lalgudi_G_Jayaraman-Violin-NP/")
for artist in artist_list:
    master_song_database = pd.DataFrame(
        columns=['song_name', 'main_artist', 'artist_listed', 'other_artist_1', 'other_artist_2', 'other_artist_3',
                 'other_artist_4',
                 'genre', 'concert_id', 'song_order', 'song_type', 'song_ragam', 'song_talam', 'composer',
                 'kalpana_swaram',
                 'neraval', 'violin_accompaniment', 'mridangam_accompaniment_1', 'mridangam_accompaniment_2',
                 'ghatam_accompaniment', 'kanjira_accompaniment', 'morsing_accompaniment',
                 'tabla_accompaniment', 'file_location', 'source'])
    table_html = bot.get_concert_list_html(artist)
    # get html of concerts
    concert_array = get_concert_links(table_html)
    # convert concert table html to array
    artist_path = create_artist_directory(artist)
    # create directory for artist

    for concert in concert_array:
        start_time = time.time()
        is_empty, _, read_me = bot.download_concerts(concert[1])
        # if concert is empty want to skip over it
        if not is_empty:
            print("waiting to complete download")
            sleep(5)
            song_list = get_recently_downloaded()
            path = create_concert_directory(artist, concert[0])
            concert_df = create_concert_database_entry(song_list, artist, concert[3], concert[2], concert[0], path)
            num_songs = 0
            for song in song_list:
                move_song_files(song, path)
                num_songs = num_songs + 1
            print "{num_songs} moved to directory. {song_list_len} songs in concert.".\
                format(num_songs=num_songs, song_list_len=len(song_list))
            write_readme(read_me, path, concert[0])
            num_concerts = num_concerts + 1
            end_time = time.time()
            time_lapsed = end_time - start_time
            time_convert(time_lapsed)
            print "{num_concerts} concerts downloaded so far".format(num_concerts=num_concerts)
            print("---------------------------------")
            print""
            master_song_database = pd.concat([concert_df, master_song_database])
        else:
            print("concert was unreachable.")
            print "{num_concerts} concerts downloaded so far".format(num_concerts=num_concerts)
            print("---------------------------------")
            print""


    filepath_excel = os.path.join(artist_path, str(artist) + ".xlsx")
    filepath_json = os.path.join(artist_path, str(artist) + ".json")
    master_song_database.to_excel(filepath_excel ,index=False, header=True)
    with open(filepath_json, 'w') as f:
        f.write(master_song_database.to_json(orient='records', lines=True))

    print "{num_concerts} concerts downloaded for {artist}".format(num_concerts=num_concerts, artist=artist)
    print "{num_songs} songs downloaded for {artist}".format(num_songs=master_song_database.shape[0], artist=artist)