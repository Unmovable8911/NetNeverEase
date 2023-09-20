import os
import eyed3
import requests
from bs4 import BeautifulSoup
from time import sleep
from sys import platform
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class Universal:
    class Error(Exception):
        pass

    class OutOfRange(Exception):
        pass

    @staticmethod
    def Return():
        raise Universal.Error

    @staticmethod
    def clear_command_line():
        """clear command line, vary by platforms"""
        if platform == 'linux' or platform == 'darwin':
            os.system('clear')
        if platform == 'win32':
            os.system('cls')


class Music:
    # Music object, contains title, artist, album, cover and id
    file = None

    def __init__(self, *, title, artist, album, cover, ID):
        """construct Music object"""
        self.title = title
        self.artist = artist
        self.album = album
        self.cover = cover
        self.ID = ID

    def alternetive_download(self):
        mp3_response = requests.get(f'https://music.163.com/song/media/outer/url/?id={self.ID}.mp3')
        mp3_response.raise_for_status()
        with open(f'{self.title}.mp3', 'wb') as mp3_file:
            mp3_file.write(mp3_response.content)

    def download(self):
        """download Music"""
        mp3_response = requests.get(f'https://link.hhtjim.com/163/{self.ID}.mp3')
        mp3_response.raise_for_status()
        with open(f'{self.title}.mp3', 'wb') as mp3_file:
            mp3_file.write(mp3_response.content)

    def save_id3_tag(self):
        """save id3 tags"""
        mp3 = eyed3.load(f'{self.title}.mp3')
        mp3.tag.title = self.title
        mp3.tag.artist = self.artist
        mp3.tag.album = self.album
        mp3.tag.images.set(3, requests.get(self.cover).content, 'image/jpeg')
        mp3.tag.save()

    def validate_mp3(self):
        try:
            mp3 = eyed3.load(f'{self.title}.mp3')
            if mp3.info.time_secs < 40.0:  # this music is not available
                return True
            else:
                return False
        except OSError:
            pass


class MusicList:
    # Both playlists and failed music lists are MusicList object
    musics = list()
    name = str()

    def add_music(self, music: Music):
        """append a Music to musics"""
        self.musics.append(music)

    def display_musics(self):
        """print out all musics in the playlist"""
        print(self.name)
        print('+', '-' * 148, '+', sep='')
        print('|', 'Number'.ljust(6), '|' 'Title'.ljust(100), '|', 'Artist'.ljust(40), '|', sep='')
        for index, music in enumerate(self.musics):  # print out the actrual content
            print('|', str(index + 1).ljust(6), '|', music.title.ljust(100), '|', music.artist.ljust(40), '|', sep='')
        print('+', '-' * 148, '+', sep='')

    def print_to_file(self):
        """print musics to Lost.txt"""
        Lost = open('Lost.txt', 'a', encoding='utf-8')  # open the file as append mode
        # print('Name'.ljust(40), 'Title'.ljust(40), 'Artist'.ljust(40), file=Lost)
        for index, music in enumerate(self.musics):
            # print the musics into the file
            if index == 0:
                print(self.name.ljust(40), f'{index + 1}'.ljust(3), music.title.ljust(100), music.artist.ljust(40), file=Lost)
            else:
                print(' '.ljust(40), f'{index + 1}'.ljust(3), music.title.ljust(100), music.artist.ljust(40), file=Lost)
        print(file=Lost)
        Lost.close()  # close the file


class Launcher:
    music_lists = list()  # this list contains all the playlists the user have
    failed = list()  # this list contains the musics failed to download

    def save_playlists(self):
        Universal.clear_command_line()  # clear command line before execute the following code
        print('--> Save Playlists')
        print('    A browser window is going to open, DO NOT CLOSE THE WINDOW!')
        print('    Login to your account in 60 seconds')

        # login
        driver = webdriver.Firefox()
        driver.get('https://music.163.com/my')
        sleep(5)
        login_button = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div[1]/a')
        login_button.click()
        try:
            login_by_other_way = login_button.find_element_by_xpath('/html/body/div[3]/div[2]/div/div[2]/div/div[3]/a')
            login_by_other_way.click()
            checkbox = login_by_other_way.find_element_by_xpath('//*[@id="j-official-terms"]')
            del login_by_other_way
        except NoSuchElementException:
            checkbox = login_button.find_element_by_xpath('//*[@id="j-official-terms"]')
        checkbox.click()
        del login_button, checkbox  # delete unusing variables to free up system memory
        sleep(60)  # login to account within this period

        # extract li elements
        driver.switch_to.frame(driver.find_element_by_css_selector('#g_iframe'))  # switch to the iframe which normally unreachable
        playlists = driver.find_element_by_xpath('/html/body/div[3]/div/div[1]/div/div[1]/ul')
        playlists = playlists.find_elements_by_tag_name('li')  # an array of lists

        # save the page source code
        Universal.clear_command_line()
        for index, li in enumerate(playlists):
            print('--> Save Playlists')
            print(f'    [{index}/{len(playlists)}] saved')
            li.click()
            sleep(3)
            name = driver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/div[1]/div[1]/div/div[2]/div/div[1]/h2').text  # name of the playlist
            with open(f'sources/{name}.html', 'w') as html:
                html.write(driver.page_source)
            print(f'    [{index + 1}/{len(playlists)}] saved')
            Universal.clear_command_line()

        driver.close()

    def manage_playlists(self):
        Universal.clear_command_line()
        sources = os.listdir('sources')  # html files in the sources directory
        print('--> Manage Playlists')
        for index, source in enumerate(sources):
            print('    ', index, ') ', source[:-5], sep='')  # print out saved page sources
        print()
        print('    00) Return')
        manage_option = input('-> ')
        if manage_option == '00':
            Universal.Return()
        else:
            input_separated = manage_option.split(' ')
            try:
                input_separated = map(lambda x: int(x), input_separated)  # convert the input into integers
            except ValueError:
                raise Universal.OutOfRange
            valid_range = range(len(sources))
            for num in input_separated:  # remove the chosen files
                if num in valid_range:
                    os.remove(f'sources/{sources[num]}')


    def load_playlists(self):
        Universal.clear_command_line()
        sources = os.listdir('sources')
        true_list = list()
        print('--> Load Playlists')
        for index, source in enumerate(sources):
            print('    ', index, ') ', source[:-5], sep='')
        print('    a) load all above')
        print()
        print('    00) Return')
        load_option = input('--> ')

        def load_all():
            nonlocal sources, true_list
            true_list = sources
        
        def load_some():
            nonlocal sources, true_list, load_option
            valid_range = range(len(sources))
            try:
                input_separated = load_option.split(' ')
                input_separated = map(lambda x: int(x), input_separated)
            except ValueError:
                raise Universal.OutOfRange
            for num in input_separated:
                if num in valid_range:
                    true_list.append(sources[num])

        load_options = {
            'a': load_all,
            'A': load_all,
            '00': Universal.Return
        }
        try:
            load_options[load_option]()
        except KeyError:
            load_some()

        # extract information
        for source in true_list:
            Universal.clear_command_line()
            with open(f'sources/{source}', encoding='utf-8') as file:
                html = file.read()
            soup = BeautifulSoup(html, 'lxml')  # make a soup
            musics = list()  # assign its value to MusicList.musics later 
            playlist = MusicList()
            playlist.name = soup.select_one('h2.f-ff2').text  # extract the name
            trs = soup.find('tbody')
            trs = trs.find_all('tr')  # musics in the playlist

            for tr in trs:
                tds = tr.find_all('td')  # index 1 contains title and ID, index 2 contains cover, index 3 contains artist, index 4 contains album
                ID = tds[1].find('a')['href'][9:]
                title = tds[1].find('b')['title'].replace('\xa0', ' ')
                cover = tds[2].find_all('span')[2]['data-res-pic']
                artist = tds[3].find('span')['title'].replace('/', ', ')
                album = tds[4].find('a')['title']

                music = Music(title=title, artist=artist, album=album, cover=cover, ID=ID)
                musics.append(music)
            playlist.musics = musics
            self.music_lists.append(playlist)
            playlist.display_musics()

    def download(self):
        """download musics"""
        true_lists = list()

        def all_playlists():
            """nearly do nothing, but that's the point, 'cause I want all playlists to be downloaded"""
            nonlocal true_lists
            true_lists = self.music_lists

        def extract_playlists_from_input():
            nonlocal download_option, true_lists
            valid_range = len(self.music_lists)
            input_separated = download_option.split(' ')
            for num in input_separated:  # extract chosen playlists
                try:
                    if int(num) in range(valid_range):
                        true_lists.append(self.music_lists[int(num)])
                except ValueError:
                    raise Universal.OutOfRange

        Universal.clear_command_line()  # clear command line before execute the following code
        print('--> Download')
        if len(self.music_lists) == 0:
            print('No playlist reserved')
            print('Login your account to extract playlists first')
            sleep(2)
            Universal.Return()
        for i, li in enumerate(self.music_lists):  # i is the index of the playlist, l is the MusicList object
            print('    ', f'{i})'.ljust(3), li.name, sep='')  # print out all the available playlists
        print('    a) Download all above')
        print()
        print('    00) Return')
        download_options = {
            'a': all_playlists,
            'A': all_playlists,
            '00': Universal.Return
        }
        download_option = input('-> ')
        try:
            download_options[download_option]()
        except KeyError:
            extract_playlists_from_input()

        musics_in_total = int()  # total number of the downloading musics
        completed_musics_in_total = int()  # number of completed musics
        for li in true_lists:  # tally up the total number of the downloading musics
            musics_in_total += len(li.musics)
        # start to download
        for li in true_lists:
            try:
                os.mkdir(li.name)  # try to make a directory with the name of the playlist
            except FileExistsError:
                pass  # do nothing if the directory has already existed
            finally:
                os.chdir(li.name)  # change to the directory in order to save the musics in respective directories
            Universal.clear_command_line()
            li.display_musics()  # have a view of all the musics in the playlist
            sleep(3)

            musics_in_current_playlist = len(li.musics)  # number of musics in the current playlist
            completed_musics_in_current = int()  # number of completed musics in current playlist

            failed_in_current = MusicList()  # store failed musics
            failed_in_current.name = li.name
            failed = list()
            # download musics in the current playlist
            for music in li.musics:
                Universal.clear_command_line()
                total_rate = round(completed_musics_in_total / musics_in_total * 100, 2)
                current_rate = round(completed_musics_in_current / musics_in_current_playlist * 100, 2)

                print(li.name)
                print('[', f'{"=" * round(total_rate):100}'.replace(' ', '-'), ']', f'  {total_rate}%', sep='')
                print('[', f'{"=" * round(current_rate):100}'.replace(' ', '-'), ']', f'  {current_rate}%', sep='')
                print(f'--> Current Music: {music.title}')
                if os.path.exists(f'{music.title}.mp3'):
                    pass  # the music has been downloaded earlier
                else:
                    try:
                        music.download()
                        music.save_id3_tag()  # save id3 tags for the music
                    except AttributeError:
                        os.remove(f'{music.title}.mp3')  # failed to download, delete the file
                        failed.append(music)
                    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, FileNotFoundError, OSError):
                        try:
                            music.alternetive_download()
                            music.save_id3_tag()
                        except AttributeError:
                            os.remove(f'{music.title}.mp3')  # failed to download, delete the file
                            failed.append(music)
                        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError, FileNotFoundError, OSError):
                            failed.append(music)
                        except UnicodeEncodeError:
                            pass
                    except UnicodeEncodeError:
                        pass
                print('    Downloaded')
                if music.validate_mp3():
                    os.remove(f'{music.title}.mp3')
                    failed.append(music)
                completed_musics_in_total += 1
                completed_musics_in_current += 1

            failed_in_current.musics = failed
            os.chdir('..')
            failed_in_current.print_to_file()
    
    def main(self):
        Universal.clear_command_line()  # clear command line before execute the following code
        print('--> Main')
        print('    1) Save Playlists')
        print('    2) Manage Playlists')
        print('    3) Load Playlists')
        print('    4) Download')
        print()
        print('    00) Quit')
        main_options = {
            '1': self.save_playlists,
            '2': self.manage_playlists,
            '3': self.load_playlists,
            '4': self.download,
            '00': exit
        }
        main_option = input('-> ')
        try:
            main_options[main_option]()
        except KeyError:
            raise Universal.OutOfRange


if __name__ == '__main__':
    while True:
        launcher = Launcher()
        try:
            launcher.main()
        except KeyboardInterrupt:
            print('-' * 80)
            print('Program iteruppted')
            sleep(2)
            exit()
        except requests.exceptions.ConnectionError:
            print('No internet connect, end program')
            sleep(2)
            exit()
        except Universal.Error:  # return to main
            continue
        except Universal.OutOfRange:
            print('-' * 80)
            print('Input out of range, end program')
            sleep(2)
            exit()
