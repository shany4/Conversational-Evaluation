# Conversation Evaluation System
## Deployment:
#### If for usage only (not for development), go to http://192.168.1.39/accounts/login and jump to the next section (Create User)


#### If for development, follow the steps below to set up the project:
Notice: your local machine must have Python and Django installed in order for the project to run
- Download the code onto your local machine.
- Open Terminal, and use the `cd` command to go to the project directory (same level as "manage.py")
- Enter `python manage.py runserver` into Terminal. You will see a similar message:

> Performing system checks...


> System check identified no issues (0 silenced).


> June 04, 2018 - 14:46:53


> Django version 1.11.13, using settings 'annotation.settings'


> Starting development server at http://127.0.0.1:8000/


> Quit the server with CONTROL-C.

- Open a web browser and type "http://127.0.0.1:8000/accounts/login" into the address bar

## Create User
 `Admin Username: admin`
 
 
 `Admin Password: rsvptech`

1. Log in as admin
2. Fill in the new user's information (username/password should be English letters only, no Chinese characters!)
   - Check the “staff” checkbox to allow the new user to upload and dispatch new tests (optional)
3. Click "Create New User". You will see the new user appear in the "Active Users" list below
4. Log out when you have finished

## Upload/Dispatch Files
### Upload
1. Log in as a staff account
2. Click on "Upload"
3. Enter a unique test case name (English letters only!) and select 基本测试
4. Choose a file:
   - please follow the template of template.xls
   - make sure you upload a `.xls` file
5. Click on "Upload"
6. Click on "Dispatch" to proceed to the Dispatch page, or "Upload" to upload a new file
  
  
### Dispatch
1. Click on "Dispatch"
2. Click on the test you want to dispatch
3. Select the user that will receive the test and enter the number of questions that will be assigned to them
4. To dispatch to additional users, click on the "+" button and follow step 3
5. Click on "Submit"

## Evaluation
1. Click on "My Tasks" 
2. Select a task and press "Enter" 
   - finished tasks will have a checkmark next to their names
   - if a finished task is selected, the page will redirect to its results
3. Select all options that apply to the question/answer pairs and click "OK"
   - click "Previous" to change your answer to previous questions
4. When finished, the results will appear. Click on "Quit" to return to the dashboard

## History:
- Choose a task from the drop-down menu
- Click on "See Result" for page to display the visual (chart) results of the 基本测试 test
   - Click on "小宝" to see results from the end of the task (stars)
- Click on "Export Result" button to download the detailed csv result
   - Make sure a task is selected before downloading
