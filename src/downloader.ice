// Downloader full interface

module Downloader {
  // List of songs
  sequence<string> SongList;
  // Allowed states for a task
  enum Status {PENDING, INPROGRESS, DONE, ERROR};
  // Clip info
  struct ClipData {
    string URL;
    Status status;
  };

  exception SchedulerAlreadyExists {};
  exception SchedulerNotFound {};
  exception SchedulerCancelJob {};

  // Handle a file transfer
  interface Transfer {
    string recv(int size);
    void end();
  };

  // Downloads scheduler
  interface DownloadScheduler {
    SongList getSongList();
    ["amd", "ami"] void addDownloadTask(string url) throws SchedulerCancelJob;
    ["ami"] Transfer* get(string song);
    // Optional
    void cancelTask(string url);
  };

  // Scheduler factory
  interface SchedulerFactory {
    DownloadScheduler* make(string name) throws SchedulerAlreadyExists;
    // Optional
    void kill(string name) throws SchedulerNotFound;
    int availableSchedulers();
  };

  // Status handling
  interface ProgressEvent {
    void notify(ClipData clipData);
  };

  // Synchronization handling
  interface SyncEvent {
    void requestSync();
    void notify(SongList songs);
  };
};
