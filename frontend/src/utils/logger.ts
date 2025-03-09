// Logger utility for the frontend
// Based on the logging pattern from helping_the_ai/main.py

// Define log levels
export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARNING = 2,
  ERROR = 3,
}

// Current log level - can be adjusted based on environment
const currentLogLevel =
  process.env.NODE_ENV === "production" ? LogLevel.WARNING : LogLevel.DEBUG;

// Logger class
class Logger {
  private module: string;

  constructor(module: string) {
    this.module = module;
  }

  private formatMessage(level: string, message: string): string {
    const timestamp = new Date().toISOString();
    return `[${timestamp}] [${level}] [${this.module}] ${message}`;
  }

  private shouldLog(level: LogLevel): boolean {
    return level >= currentLogLevel;
  }

  debug(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.debug(this.formatMessage("DEBUG", message), ...args);
    }
  }

  info(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.info(this.formatMessage("INFO", message), ...args);
    }
  }

  warn(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.WARNING)) {
      console.warn(this.formatMessage("WARNING", message), ...args);
    }
  }

  error(message: string, error?: Error, ...args: any[]): void {
    if (this.shouldLog(LogLevel.ERROR)) {
      console.error(this.formatMessage("ERROR", message), error, ...args);
    }
  }
}

// Factory function to create a logger for a specific module
export function getLogger(module: string): Logger {
  return new Logger(module);
}

// Default logger
export default getLogger("app");
