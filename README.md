# Development

## Converting *.ui into *.py

```shell script
$ cd capybara_tw/gui/ 
$ pyuic5 --from-imports -o main_window.py main_window.ui
```

## Converting *.qrc into *.py

```shell script
$ cd capybara_tw/gui/ 
$ pyrcc5 -o resources_rc.py resources.qrc 
```

## Doing both above

```shell script
$ ./gen-gui.sh
```
