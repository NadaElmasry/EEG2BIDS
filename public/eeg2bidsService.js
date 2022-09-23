const {spawn} = require('child_process');
const os = require('os');
const pythonLog = require('electron-log');
    
/**
 * EEG2BIDS Wizard Service
 */
module.exports = class EEG2BIDSService {
  /**
   * constructor
   */
  constructor() {
    this.platform = os.platform(); // darwin or win32.
    this.process = null; // the service process.
    pythonLog.transports.file.fileName = 'python.log';
  }

  /**
   * startup the service process
   */
  async startup() {
    const pathToService = require('path').join(
        __dirname,
        '..',
      this.platform === 'win32' ?
        'dist/eeg2bids-service-windows.exe' :
        'dist/eeg2bids-service.app/Contents/MacOS/eeg2bids-service',
    );

    this.process = spawn(pathToService, []);

    this.process.stdout.on('data', function (data) {
      pythonLog.info(data.toString());
    });

    this.process.stderr.on('data', function (data) {
      pythonLog.error(data.toString());
    });

    this.process.on('exit', function (code) {
      pythonLog.info('Python process exited with code ' + code.toString());
    });
  }

  /**
   * shutdown the service process
   */
  shutdown() {
    if (this.process) {
      console.info('[SHUTDOWN of eeg2bidsService]');
      // this.process.kill();
      this.process = null;
    }
  }
};
