import json
import sys
import time
from datetime import datetime
from datetime import timedelta
import os

def task_updater(json_data, current_time, file_path):
    for task in json_data:
        freq_int = task['freq int']
        freq_type = task['freq type']

        reset_datetime_str = task['reset datetime']
        reset_datetime = datetime.strptime(reset_datetime_str, "%Y-%m-%dT%H:%M:%S")

        if freq_type == 'hours':
            freq_delta = timedelta(hours=freq_int)
        elif freq_type == 'days':
            freq_delta = timedelta(days=freq_int)
        elif freq_type == 'weeks':
            freq_delta = timedelta(weeks=freq_int)

        if reset_datetime < current_time:
            task['completed'] = "no"
            with open(file_path, 'w') as file:
                json.dump(json_data, file, indent=4)

        while reset_datetime < current_time:
            reset_datetime += freq_delta

        task['reset datetime'] = reset_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        
        with open(file_path, 'w') as file:
            json.dump(json_data, file, indent=4)

def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{file_path}'.")
        return None

def help():
    print("Help [command]")
    print("New")
    print("Delete OR Del")
    print("Sort")
    print("Complete OR Comp OR C")
    print("Uncomplete OR Uncomp OR Un")
    print("ShowID OR ID")
    print("List OR Tasks")

def query_task(json_data, task_id):
    for task in json_data:
        if 'id' in task and task['id'] == task_id:
            return task
    return None

def delete_task(json_data, task_id):
    for index, task in enumerate(json_data):
        if 'id' in task and task['id'] == task_id:
            del json_data[index]

            for shifted_task in json_data[index:]:
                shifted_task['id'] -= 1

            return True
    return False

def complete_task(json_data, task_id, file_path):
    for task in json_data:
        if 'id' in task and task['id'] == task_id:
            task['completed'] = "yes"
            with open(file_path, 'w') as file:
                json.dump(json_data, file, indent=4)
            return True
    return False

def uncomplete_task(json_data, task_id, file_path):
    for task in json_data:
        if 'id' in task and task['id'] == task_id:
            task['completed'] = "no"
            with open(file_path, 'w') as file:
                json.dump(json_data, file, indent=4)
            return True
    return False

def showid(json_data):
        for task in json_data:
            if "id" in task:
                print(f"{task['id']} || {task['name']}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'Tasks.json')
    json_data = read_json(file_path)

    if json_data is None:
        time.sleep(5)
        sys.exit() 

    while True:
        current_time = datetime.now()
        task_updater(json_data, current_time, file_path)
        print()
        print("Waiting for input. Type `help` for list of commands.")
        print()
        command = input().strip().lower()
        print()        
        
        if command.startswith('help'):
            parts = command.split()
            if len(parts) == 1:
                help()
                continue
            elif len(parts) == 2:
                if parts[1] == "new":
                    print("Creates a new task. Will walkthrough.")
                if parts[1] == "delete" or parts[1] == "del":
                    print("Deletes task. Uses the task ID. Asks for comfirmation.")
                if parts[1] == "showid" or parts[1] == "id":
                    print("Prints the ID and Name of each task.")
                    print("Alternitvely, just look in the json.")
                if parts[1] == "sort":
                    print("Re-orders the tasks by their id.")
                if parts[1] == "complete":
                    print("Marks a task as completed.")
                if parts[1] == "uncomplete":
                    print("Marks a task as uncomplete.")
                if parts[1] == "list" or parts[1] == "tasks":
                    print("Lists all tasks")
                if parts[1] == "help":
                    print("Really? You really asked for help about the help command?")

        elif command == "new":
            print("Enter the task name.")
            print()
            task_name = input().strip().lower()
            print()
            print("Enter the task date and time in the form of:")
            print("YYYY/MM/DD HH:MM:SS")
            print()
            task_datetime_str = input().strip().lower()
            task_datetime = datetime.strptime(task_datetime_str, "%Y/%m/%d %H:%M:%S")
            print()
            print("Enter a frequency interval in the form of:")
            print("'Number' 'Hours/Days/Weeks'")
            print()
            task_frequency = input().strip().lower()
            parts = task_frequency.split()
            if len(parts) == 2:
                freq_int = int(parts[0])
                freq_type = parts[1]

            new_id = max(task.get('id', 0) for task in json_data) + 1
            new_task = {
                "id": new_id,
                "name": task_name,
                "reset datetime": task_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
                "freq int": freq_int,
                "freq type": freq_type,
                "completed": "no"
            }
            print()
            print("Adding new task.")
            json_data.append(new_task)
            with open(file_path, 'w') as file:
                json.dump(json_data, file, indent=4)

        elif command == "sort":
            showid(json_data)
            print()
            print("Type the order of the new task ID's in the form:")
            print("1 3 2 4")
            print()
            new_order_input = input().strip()
            new_order_ids = [int(id) for id in new_order_input.split() if id.isdigit()]

            if len(new_order_ids) == len(json_data):
                id_task_mapping = {task['id']: task for task in json_data}
                json_data = [id_task_mapping[id] for id in new_order_ids]
                for index, task in enumerate(json_data):
                    task['id'] = index + 1
                with open(file_path, 'w') as file:
                    json.dump(json_data, file, indent=4)
                print()
                print("Tasks rearranged successfully")
            else:
                print("Woops. Incorrect somehow. :)")
            
        elif command == "delete" or command == "del":
            showid(json_data)
            print()
            print("Enter the task ID to delete")
            print()
            task_id_input = input().strip()
            if task_id_input.isdigit():
                task_id = int(task_id_input)

                task_to_kill = query_task(json_data, task_id)
                if task_to_kill:
                    print()
                    print("This is task")
                    print(f"{task_to_kill['id']} || {task_to_kill['name']}")
                    print("Are you sure you want to delete this task? Type 'Yes' to confirm.")
                    print()
                    del_con = input().strip().lower()
                    print()
                    if del_con == "yes":
                        print("Deleting Task",task_id)
                        if delete_task(json_data, task_id):
                            print("Task deleted.")
                            with open(file_path, 'w') as file:
                                json.dump(json_data, file, indent=4)
                        task_to_kill = None
                    else:
                        print("Not confirmed.")
                else:
                    print("Task ID not found.")
            else:
                print("Not a digit.")

        elif command == "showid" or command == "id":
            showid(json_data)
        
        elif command == "list" or command == "tasks":
            for task in json_data:
                completion_status = "completed" if task['completed'].lower() == "yes" else "not completed"
                print(f"{task['name']} || {task['reset datetime']} || {task['freq int']} {task['freq type']} || {completion_status}")

        elif command == "complete" or command == "c" or command == "comp":
            showid(json_data)
            print()
            print("Enter the task ID to complete")
            print()
            task_id_input = input().strip()
            print()
            if task_id_input.isdigit():
                task_id = int(task_id_input)

                task_to_complete = query_task(json_data, task_id)
                if task_to_complete:
                    print("Completing task", task_id)
                    if complete_task(json_data, task_id, file_path):
                        print("Task", task_id, "completed")

        elif command == "uncomplete" or command == "un" or command == "uncomp":
            showid(json_data)
            print()
            print("Enter the task ID to uncomplete")
            print()
            task_id_input = input().strip()
            print()
            if task_id_input.isdigit():
                task_id = int(task_id_input)

                task_to_uncomplete = query_task(json_data, task_id)
                if task_to_uncomplete:
                    print("Unompleting task",task_id)
                    if uncomplete_task(json_data, task_id, file_path):
                        print("Task", task_id, "uncompleted")

        elif command == "exit" or command == "quit" or command == "die":
            print("Goodbye!")
            sys.exit()

        else:
            print("Not a command")
            print("Or you typed the command wrong")
            print("Or I messed up the code. :)")

if __name__ == "__main__":
    main()
