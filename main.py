from notion.client import NotionClient
from todo_list_mgr import todo_list_mgr
from configparser import ConfigParser


def main():
    config = ConfigParser()
    config.read("config.ini")
    client = NotionClient(token_v2=config.get("Default", "API_KEY"))

    todo_mgr = todo_list_mgr(client, config.get("Default", "todo_page"))
    todo_mgr.fresh_list()


if __name__ == "__main__":
    main()
