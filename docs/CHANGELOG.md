
# CHANGELOG
This document provides a high-level log of changes for each version of the project. Each module has a dedicated section that lists the changes in a version-wise manner. For main updates, please refer to the README.md file.


## Detailed Update Logs

### baidu_cloud_uploader.py 1.3.4
- **v1.3.4**
  - 优化了代码结构，提高了日志系统的可配置性。
- **v1.3.3**
  - 代码重构，增加用户提示等。
- **v1.0.0**
  - 实现上传百度云盘的基本功能。

### config_loader.py 1.4.1
- **v1.4.0**
  - 添加了对缺失环境变量的默认值和错误处理。
- **v1.3.0**
  - 在所有环境变量参数中添加了对应的中文解释。

### deploy.sh v1.3.0
- **v1.3.0**
  - 代码重构，构造函数及更多环境检测。
- **v1.2.0**
  - 代码更新，增加了虚拟环境等变量。
- **v1.0.0**
  - 初始版本，用于linux环境部署。

### downloader_checker.py v2.4.1
- **v2.4.0**
  - 更新了代码，引入了更多的错误处理和日志记录。
- **v2.1.3**
  - 引入了DownloaderManager类，用于管理视频的下载和检查。
- **v1.2.2**
  - 添加了日志配置，确保与其他日志文件保持一致。
  - 修正了配置键名的大小写不一致问题。

### link_extractor.py v1.4.1
- **v1.4.0**
  - 优化了代码，增加了更多的错误处理和日志记录。
- **v1.0.1**
  - 添加了logger对象和对`extract_video_links_from_page`函数的错误处理。

### metadata_manager.py v1.3.3
- **v1.3.0**
  - 代码更新，增加了更多的错误处理和日志记录。
- **v1.0.1**
  - 初始版本，用于管理视频的元数据。

### notifier.py v1.4.2
- **v1.4.0**
  - 更新了代码，添加了命令行参数的处理。
- **v1.1.1**
  - 修复了电子邮件格式问题。
  - 添加了更多的日志记录。

### scheduler.py v1.3.0
- **v1.3.0**
  - 更新了代码，优化了任务调度逻辑和错误处理。
- **v1.0.3**
 - 为 ‘scheduler’ 模块添加了 logger 对象。
 - 从配置文件中集成了调度时间。
 - 为 BlockingScheduler 添加了一个监听器，以便更好地记录日志。
- **v1.0.2**
 - 修复了导入和调度时间，用于上午9:00和下午9:00的运行。
- **v1.0.1**
 - 添加了一个 --test 标志，用于测试目的的立即执行。
- **v1.0.0**
 - 初始版本，带有调度器，用于自动化视频下载和通知过程。

### utils.py v1.4.1
- **v1.4.0**
  - 添加了新的辅助函数和错误处理。
- **v1.1.0**
  - 添加了多个实用函数，如`create_directories`, `setup_logging`, `sanitize_filename`。

### video_downloader.py v1.9.1
- **v1.9.0**
  - 代码经过重构，增加了更多的错误处理和日志记录。
- **v1.6.1**
  - 引入了`LinkExtractor`类来专门处理链接的提取工作。
  - 新增了`schedule_runner`函数，支持根据设定的时间自动运行下载任务。
  - 日志记录逻辑得到了进一步优化，以更方便地捕获和查看关键信息。
  - 整体代码结构进行了优化，提高了代码的可读性和可维护性。
- **v1.6.0**
  - 重新组织了错误处理逻辑，使其更具有针对性，可以捕获网络超时、连接失败等具体错误。
  - 加入了`logger`对象，对于关键的信息和错误进行了日志记录。
  - 在`extract_video_links_from_page`中添加了更细致的错误处理。
  - `DownloaderManager`类被引入，用于管理视频的下载和检查。
- **v1.5.3**
  - 重构了`sanitize_filename`函数，确保对所有特殊字符进行了处理。
  - `MetadataManager`类被引入，提供了更方便的方式来存储和管理视频元数据。
  - 对视频信息进行的检查被加强，确保只下载那些还没有被下载的视频。
  - 在下载每一个视频后，都会存储该视频的元数据。
- **v1.5.2**
  - 重构了代码，将`create_directories`, `setup_logging`, `sanitize_filename`, `extract_video_links_from_page`等函数剥离到`utils.py`。
  - 其他一些小的改进和优化。

### youtube_metadata_checker.py v1.0.2
- **v1.0.0**
  - 实现youtube API和yt-dlp下载视频元数据。

Note: For main updates, please refer to the README.md file.
