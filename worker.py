#!/usr/bin/env python

from multiprocessing import Process
from subprocess import call
from selenium import webdriver
import tempfile
import shutil
import os

# TODO -- Add these to config
username = ""
access_key = ""
selenium_host = "localhost"
selenium_port = 8045

command_executor = "http://%s:%s@%s:%s/wd/hub"%(username, access_key, selenium_host, selenium_port)

def get_desired_capabilities(browser_name):
    browser_info = browser_name.split(" ", 2)
    dc = getattr(webdriver.DesiredCapabilities, browser_info[0].upper())
    if len(browser_info) > 1:
        dc['version'] = str(browser_info[1])
        if dc["version"] == "9" and dc["platform"] == "WINDOWS":
            dc["platform"] = "VISTA"
    if dc["browserName"] == "opera":
        dc["platform"] = "LINUX"
    return dc

def make_thumbnail(filename, thumbnail_filename):
    call([
       "convert",
       filename,
       "-thumbnail", "300x800",
       thumbnail_filename
    ])

def make_screenshot(url, filename, browser_name):
    savedir = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:
        pass

    print "starting browser:%s url:%s filename:%s" % (browser_name, url, filename)
    tmp_filename = "%s/screenshot-%s.tmp.png" % (savedir, browser_name)
    dc = get_desired_capabilities(browser_name)
    print "desired capabilities: %s" % dc
    browser = webdriver.Remote(command_executor=command_executor,
            desired_capabilities=dc)
    browser.get(url)
    browser.execute_script("window.resizeTo(1280, 1024);")
    #browser.wait_for_page_to_load(10000)
    browser.get_screenshot_as_file(tmp_filename)
    call(["convert", tmp_filename,
        "-gravity", "North", "-background", "YellowGreen", "-splice", "0x18",
        "-annotate", "+0+2", browser_name,
          filename
    ])
    os.remove(tmp_filename)
    browser.quit()
    shutil.rmtree(savedir)
    return filename

def combine_images(tmp_dir, filename):
    call(["montage",
        "-label", "%f",
        "-background", "#000000",
        "-mode", "concatenate",
        #"-geometry", "+40+40>",
        #"-tile", "3x2",
        "-border", "20",
        "%s/screenshot-*.png" % tmp_dir,
        "static/"+filename])
    return filename

