import argparse
import random
import os
import pdb
import time
import sys
import uuid

import requests
from dotenv import load_dotenv
from lxml import html

from logger import get_logger
from settings import THIS_DIR, IMG_DIR


logger = get_logger(__name__)

logger.info("Loading environment variables")
load_dotenv()


if os.getenv("USERNAME") is None:
    logger.error("USERNAME not set as environment variable.")
    sys.exit(1)


if os.getenv("PASSWORD") is None:
    logger.error("PASSWORD not set as environment variable.")
    sys.exit(1)


if not os.path.exists(IMG_DIR):
    logger.info(" creating %s" % IMG_DIR)
    os.mkdir(IMG_DIR)


def image_name(link):
    ext = link.split(".")[-1]
    name = "%s.%s" % (uuid.uuid4().hex, ext)
    return name


def downloader(file_name, session):
    with open(file_name, "r") as ts:
        links = ts.readlines()
    
    for each in links:
        each = each.strip("\n")
        bites = session.get(each)

        if bites.status_code == 200:
            with open(os.path.join(IMG_DIR, image_name(each)), "wb") as ts:
                ts.write(bites.content)
                ts.close()
                logger.info(" %s saved" % each)
                continue
        else:
            logger.info(
                "Unable to download image %s status code %s" % (
                    each, 
                    bites.status_code
                )
            )


def main(args):
    url = args.url.rstrip("/")
    blog_name = url.replace("https://", "").rstrip("/").split(".")[0]
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    end_page = args.end
    start_page = args.start
    random_pause = args.random_pause
    streak_limit = int(args.streak_limit)
    tags = args.tags or []
    tag_method = args.tag_method.lower()
    if tag_method not in ["and", "or"]:
        raise SystemExit("Only AND or OR for tag method allowed.")
    if tags:
        if isinstance(tags, str):
            tags = [
                tags,
            ]
        tags = [t.strip().lower().replace("#", "") for t in tags]
    if tags:
        logger.info(
            f'[{blog_name}] {tag_method.upper()}ing posts with tags: {", ".join(tags)}',
        )
    else:
        logger.info(f"[{blog_name}] No tags set, grabbing all posts")
    tags_str = "_{tag_method}_".join(tags)
    output = args.output
    max_images = int(args.max_images)

    session = requests.Session()
    login_page = html.fromstring(session.get("https://bdsmlr.com/login").text)
    login_hidden_value = login_page.xpath('//*[@class="form_loginform"]/input[@type="hidden"]/@value')[0]
    
    form_values = {"email": username, "password": password, "_token": login_hidden_value}
    rv = session.post("https://bdsmlr.com/login", data=form_values)
    if rv.ok:
        logger.info(f"[{blog_name}] Logged in ...")

    def get_image_links(page, tags=None, tag_method="or"):
        images_srcs = []
        posts = page.xpath('//div[@class="searchpost"]')
        for post in posts:
            imgs = []
            for img in post.cssselect("img"):
                for value in img.values():
                    # technically could use .attrib['src']?
                    imgs.append(value.strip())
            if tags:
                post_tags = [
                    t.text_content().strip().replace("#", "")
                    for t in post.cssselect("a.tag")
                ]
                if tag_method == "or":
                    if any([t in post_tags for t in tags]):
                        images_srcs.extend(imgs)
                else:
                    if all([t in post_tags for t in tags]):
                        images_srcs.extend(imgs)
            else:
                images_srcs.extend(imgs)
        return images_srcs

    if not output:
        output_file = f"blog_{blog_name}.txt"
        if tags:
            tags_str = "_".join(tags)
            output_file = f"blog_{blog_name}__{tags_str}.txt"
    else:
        output_file = output

    # Get true end page, adjust accordingly
    page = html.fromstring(session.get(f"{url}/archive", timeout=300).text)
    page_numbers = page.xpath('//li[@class="page-item"]/a/text()')

    ###############################################################################
    # For some reason on blogs it just never finds true end page, catch except here
    ###############################################################################

    try:
        true_end_page = list(map(int, filter(str.isnumeric, page_numbers)))[-1]
    except Exception as error:
        true_end_page = None
    if end_page:
        if end_page > true_end_page:
            end_page = true_end_page
    else:
        end_page = true_end_page

    image_count = 0
    current_streak = 0
    current_page = start_page
    done = False
    logger.info(f"[{blog_name}] Getting {blog_name} ({url}) archive ...")
    while not done:
        logger.info(f"[{blog_name}] Fetching images, page {current_page}/{end_page} ...")
        page = html.fromstring(
            session.get(
                f"{url}/archive", params={"page": current_page}, timeout=300
            ).text
        )
        links = get_image_links(page, tags, tag_method)
        if max_images:
            if image_count >= max_images:
                logger.info(f"[{blog_name}] Reached max image count of {max_images}")
                done = True
                continue
            if (image_count + len(links)) > max_images:
                cutoff = len(links) - ((image_count + len(links)) - max_images)
                links = links[:cutoff]
                image_count += len(links)
                done = True
            else:
                image_count += len(links)

        total = len(links)
        if total > 0:
            current_streak = 0
        else:
            current_streak += 1

        if current_streak >= streak_limit:
            logger.info(f"[{blog_name}] Ending scrape, met empty page streak!")
            done = True

        links_text = "\n".join(links) + "\n"
        if max_images:
            image_count_str = f", {image_count}/{max_images}"
            logger.info(
                f"[{blog_name}] Found {total} images on page {current_page}{image_count_str} (NS: {current_streak})"
            )
            if done and (image_count >= max_images):
                logger.info(f"[{blog_name}] Reached max image count of {max_images}")

        if links:
            with open(output_file, "a") as f:
                f.write(links_text)

        if end_page:
            if current_page >= end_page:
                done = True
                continue

        if random_pause:
            time.sleep(random.randint(0, 5))

        current_page += 1

    logger.info(f"[{blog_name}] Done! Collected {image_count} over {current_page} page(s)!")

    logger.info(" Downloading images!") 
    downloader(output_file, session)

    logger.info(" Cleanup ...")
    os.unlink(output)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BDSMLR Blog parser"
    )
    parser.add_argument(
        "url", 
        type=str, 
        help="Url of the blog to scrape"
    )
    parser.add_argument(
        "-s", 
        "--start", 
        type=int, 
        default=1
    )
    parser.add_argument(
        "-e", 
        "--end", 
        type=int, 
        default=None
    )
    parser.add_argument(
        "--random-pause", 
        default=False, 
        action="store_true"
    )
    parser.add_argument(
        "--streak-limit",
        default=25,
        help="how many empty pages to go through before we give up",
    )
    parser.add_argument(
        "-t", 
        "--tags", 
        default=None, 
        nargs="*"
    )
    parser.add_argument(
        "-m",
        "--tag-method",
        default="or",
        help="method for tag requirements, AND or OR",
    )
    parser.add_argument(
        "-o", 
        "--output", 
        default=os.path.join(THIS_DIR, "output.txt")
    )
    parser.add_argument(
        "-x", 
        "--max-images", 
        default=None, 
        type=int, 
        help="maximum images to pull"
    )
    args = parser.parse_args()
    main(args)
