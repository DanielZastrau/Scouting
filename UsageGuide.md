# Usage

Install python
---------------------------------------------------------------------------------------------------

You will need to install python3.14 from the official python website.
*     https://www.python.org/

Inside a powershell
---------------------------------------------------------------------------------------------------

Create a virtual environment and activate it.
*     py -m venv ./venv
*     ./venv/Scripts/activate

Install from the requirements.txt.
*     py -m pip install -r requirements.txt

Then inside the scouting folder create a .txt file and scout the team you want according to GuideForNotation.md. To generate the pdf, lastly execute `pipe.ps1`.
*     .\pipe.ps1