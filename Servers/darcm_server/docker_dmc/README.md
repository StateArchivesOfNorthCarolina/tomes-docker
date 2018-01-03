# DarcMailCLI v0.9.0
This is a fork of Carl Shaefer's (Smithsonian Institution Archives) 
CmdDarcMailXml.  My goal with this refactor is to modularize the
tool, and add some functionality.

As of this version DarcMailCLI produces valid EAXS xml in a single 
file or multiple chunked files if the attachments are stored externally.

As of this version DarcMailCLI can accept email accounts in EML
form.

It also produces, optionally, a serialized JSON version of an EAXS
encoded account.

Added a config.yml file.  Currently it only takes one path where the
output of DarcMailCLI will be.

# Requirements
* Python 3
* lxml
* yaml
* json

# Basic Usage
DarcMailCLI.py -a [Name of Account] -d [Path to the MBOX or EML structure] 
                
DarcMailCLI.py -a 'GovernorPerdue' -d 'C:\\Repository\\Perdue\\'

## Options
    -c [integer]    Number of messages per file.
    -fe             Switch: indicates that the source emails are in .eml format
    -j              Switch: produces serialized JSON

"# docker_dmc" 
