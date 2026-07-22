# Case Study: Organizing the Downloads Folder

A system administrator managed several shared computers in a small office. Each Downloads folder accumulated thousands of files with no criteria: old installers, screenshots, invoice PDFs, half-downloaded torrents, and duplicate documents. Sorting everything manually took hours every month, and it was easy to accidentally delete something important.

With Desktop Automation Toolkit, they defined an automate_rules.json file with simple rules: automatically delete any .torrent, move images (.jpg, .png, .gif) to an "Images" folder, and leave invoice PDFs untouched in a "Documents" folder. Before applying the changes, they used the --dry-run mode of the organize command to review exactly which files would be moved or deleted, without risking accidental data loss.

A folder with over 2,000 mixed files was organized in seconds, with a clutter reduction close to 95%. The same rule configuration is now reused on all office computers, and the cleanup that used to take an entire afternoon now runs with a single command.
