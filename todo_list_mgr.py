from notion.client import NotionClient
from notion.collection import NotionDate
from datetime import datetime, timedelta
from math import ceil


class todo_list_mgr:

    def __init__(self, client, page_to_update):
        assert(isinstance(client, NotionClient))
        self.target_view = client.get_collection_view(page_to_update)
        self.task_mgr = task_mgr()

    def fresh_list(self):
        print("Current Run Start Time: " + str(datetime.now()))
        for row in self.target_view.collection.get_rows():
            self.task_mgr.update(row)


class task_mgr:
    """
    Used for Notion template
    """

    @staticmethod
    def __is_valid(row):
        try:
            _ = row.Interval + str(row.Done) + str(row.Scheduled)
            return True
        except:
            return False

    @staticmethod
    def __is_recurring(row):
        if row.Interval == "":
            return False
        else:
            return True

    @staticmethod
    def __is_done(row):
        return row.Done

    @staticmethod
    def __is_due(row):
        sys_time = datetime.today().date()
        due_time = row.Scheduled

        if isinstance(due_time.start, datetime):
            due_time = due_time.start.date()
        else:
            due_time = due_time.start

        if (due_time - sys_time).days < 0:
            return True
        else:
            return False

    @staticmethod
    def __update_next_due(row):
        interval = int(row.Interval)
        last_start = row.Scheduled.start
        today = datetime.today().date()
        start_to_now_days = (today - last_start).days
        next_day = last_start + timedelta(days=ceil(start_to_now_days / interval) * interval)

        row.Scheduled = NotionDate(start=next_day)
        row.Done = False

    def __update_timeline(self, row):
        if row.Scheduled == None:
            print("No scheduled time set! Skipping...")
            return

        scheduled_time = row.Scheduled.start
        sys_date = datetime.strptime(
            str(datetime.today().date()), '%Y-%m-%d')
        # new week start from Monday
        # delta = timedelta((12 - sys_date.weekday()) % 6)
        next_seven_date = (sys_date + timedelta(7)).date()
        next_thirty_day_date = (sys_date + timedelta(30)).date()

        if isinstance(scheduled_time, datetime):
            scheduled_time = scheduled_time.date()

        if self.__is_done(row):
            result = "Completed"
        elif self.__is_due(row):
            result = "Delay"
        elif (scheduled_time - sys_date.date()).days == 0:
            result = "Today"
        elif (scheduled_time - next_seven_date).days <= 0:
            result = "Next 7 day"
        elif (scheduled_time - next_thirty_day_date).days <= 0:
            result = "Next 30 day"
        else:
            result = "later"

        if result != row.Timeline:
            row.Timeline = result
            print("Task moved to " + row.Timeline)
        else:
            print("Timeline not changed")

    def update(self, row):
        print("------------------------------------")
        print("Processing Task with name : " +
              row.get_property("Task Name"))
        if self.__is_valid(row) and self.__is_recurring(row):
            if not self.__is_due(row):
                print("Task should be completed in the future, skipping...")
            else:
                if self.__is_done(row):
                    print("Task is done, update the next due time")
                    self.__update_next_due(row)
                else:
                    print("Task is due but not finished, skipping...")
        else:
            print("Not recurring task or the task is not valid, skipping")

        # refresh task and update timeline info
        self.__update_timeline(row)


