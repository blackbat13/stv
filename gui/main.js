const { app, BrowserWindow, ipcMain, screen, dialog } = require('electron');
// Zachowaj globalną referencję obiektu okna, jeśli tego nie zrobisz, okno
// zostanie zamknięte automatycznie, gdy obiekt JavaScript odśmieci pamięć.
let win;

function createWindow() {
    // Stwórz okno przeglądarki.
    let rect = getWindowRect();
    win = new BrowserWindow({
        width: rect.width,
        height: rect.height,
        x: rect.x,
        y: rect.y,
        webPreferences: {
            nodeIntegration: true,
        },
    });
    win.setSize(rect.width, rect.height);

    // i ładowanie index.html aplikacji.
    win.loadFile('index.html');

    // Otwórz Narzędzia Deweloperskie.
    // win.webContents.openDevTools();


    // Emitowane, gdy okno jest zamknięte.
    win.on('closed', () => {
        // Dereference the window object, usually you would store windows
        // in an array if your app supports multi windows, this is the time
        // when you should delete the corresponding element.
        win = null;
    });
    
    ipcMain.on("toggle-devtools", () => toggleDevTools());
    
    ipcMain.on("choose-model-file", (event, args) => {
        let msgKey = args[0];
        let lastFilePath = args[1];
        let title = args[2];
        dialog.showOpenDialog(win, {
            properties: ["openFile"],
            title: title,
            defaultPath: lastFilePath || undefined,
        }).then(result => {
            let filePath = result.canceled || !result.filePaths ? null : result.filePaths[0];
            event.reply("model-file", [msgKey, filePath]);
        });
    });
}

function toggleDevTools() {
    if (win) {
        win.webContents.toggleDevTools();
    }
}

function getWindowRect() {
    const { x, y } = screen.getCursorScreenPoint();
    const currentDisplay = screen.getDisplayNearestPoint({ x, y });
    
    let windowWidth = Math.round(currentDisplay.workArea.width * 0.75);
    let windowHeight = Math.round(currentDisplay.workArea.height * 0.75);
    let windowX = Math.round(currentDisplay.workArea.x + (currentDisplay.workArea.width - windowWidth) / 2);
    let windowY = Math.round(currentDisplay.workArea.y + (currentDisplay.workArea.height - windowHeight) / 2);
    
    return {
        x: windowX,
        y: windowY,
        width: windowWidth,
        height: windowHeight,
    }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow);

// Zamknij, gdy wszystkie okna są zamknięte.
app.on('window-all-closed', () => {
    // On macOS it is common for applications and their menu bar
    // to stay active until the user quits explicitly with Cmd + Q
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (win === null) {
        createWindow();
    }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.