// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
var PythonShell = require('python-shell');

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

    // The command has been defined in the package.json file
    // Now provide the implementation of the command with  registerCommand
    // The commandId parameter must match the command field in package.json
    let disposable = vscode.commands.registerCommand('extension.sendToClarisse', () => {
        // The code you place here will be executed every time your command is executed
        var config=vscode.workspace.getConfiguration("clarissecommandport");
        var host = config.get("host");
        var port = config.get("port");
        var editor = vscode.window.activeTextEditor;
        var selection = editor.selection;
        var text;
        if (selection.isEmpty != true )
        {
            text = editor.document.getText(selection);
        }
        else
        {
            text=editor.document.getText();
        }
        var options = {
            mode: 'text',
            args: [host, port, text]
        };
        var pyshell = new PythonShell(context.extensionPath.concat("/src/test.py"), options);

        pyshell.on('message', function (message) {
            if(message.includes("Error")){
                vscode.window.showErrorMessage(message);
            }
            else{
                console.log(message)
                vscode.window.showInformationMessage(message);
            }
        });

    });

    context.subscriptions.push(disposable);
}

// this method is called when your extension is deactivated
export function deactivate() {
}