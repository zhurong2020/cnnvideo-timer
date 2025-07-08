# CNN Video Timer
CNN Video Timer is a tool designed for scheduling the checking and downloading of videos from CNN, with automated link extraction, video downloading, and timed task execution, complemented by email notifications upon download completion. 

## 功能介绍
CNN Video Timer 是一个用于定时检查和下载 CNN 视频的工具。它能自动提取CNN10的英语新闻Youtube视频链接，下载视频，并且可以配置为定时执行这些任务。下载完成后，它还可以通过电子邮件发送通知。

本项目在计划重构，添加实现更多功能，新项目链接不日将发布。

## 文件结构

项目现在遵循更规范的结构：

-   `.gitignore`：排除文件包括，日志，元数据，下载视频，本地配置，密钥，临时文件，虚拟环境等。
-   `config/`：包含配置文件。
    -   `configenv`：参考配置文件，需要更名为 `config.env`，并设置相应的参数。
-   `docs/`：包含所有项目文档。
    -   `CHANGELOG.md`：各模块版本更新记录。
    -   `FAQ.md`：常见问题解答，特别是Linux安装问题。
    -   `LICENSE.md`：MIT许可证详情。
    -   `README.md`：英文版说明文档。
    -   `README_CN.md`：中文版说明文档。
-   `scripts/`：包含部署和构建脚本。
    -   `deploy.sh`：Linux Ubuntu 一键安装脚本，用于自动部署项目。
    -   `install.bat`：Windows 用户安装脚本。
    -   `build.bat`：给管理员使用的打包模块。
-   `src/`：包含所有 Python 源代码。
    -   `baidu_cloud_uploader.py`：百度云上传模块。
    -   `config_loader.py`：配置加载模块。
    -   `downloader_checker.py`：下载检查器模块。
    -   `link_extractor.py`：链接提取模块。
    -   `metadata_manager.py`：元数据管理模块。
    -   `notifier.py`：通知模块。
    -   `scheduler.py`：调度器模块。
    -   `utils.py`：实用工具模块。
    -   `video_downloader.py`：视频下载器模块。
    -   `youtube_metadata_checker.py`：YouTube 元数据检查器模块。
-   `venv/`：Python 虚拟环境（已被 Git 忽略）。
-   `requirements.txt`：项目依赖。
-   `bin/`：存放第三方工具，目前为`ffmpeg.exe`，`ffprobe.exe``ffplay.exe`。
-   `log/`：存放日志文件，日志文件名为`video_downloader.log`。
-   `metadata/`：存放下载视频的元数据信息，元数据名为`metadata.json`。
-   `videos/`：存放下载的视频文件，各日期的视频文件。

## 更新日志
请查看 `docs/CHANGELOG.md` 文件以获取详细的更新日志。

## 依赖
-   Python 3
-   FFmpeg，请下载ffmpeg.exe后放在本项目的`bin`子目录中，下载网址：https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
-   其他 Python 库：apscheduler, python-dotenv, requests, yt_dlp，具体版本号请参考 `requirements.txt` 文件。

## 如何使用
### Windows
#### 方法一（推荐）
1.  直接下载https://github.com/znhskzj/cnnvideo-timer/releases/download/v0.9.1/cnn10vd_setup.exe
2.  运行已经下载到本地的exe文件，按照步骤完成安装即可，会生成开始菜单中的程序组和桌面图标（如果选择）。

#### 方法二
1.  直接下载：https://github.com/znhskzj/cnnvideo-timer/releases/download/v0.9.1/releaseffmpeg.zip
2.  在本地新建一个目录，将上述文件解压缩。
3.  执行 `scripts/install.bat` 脚本（Windows 10 以上用户，如果 Windows 10 以下，需要自行安装解压缩软件并参照以下方法三）。

#### 方法三
1.  在 https://github.com/zhurong2020/cnnvideo-timer 的仓库中，release 页面下载最新版本。
2.  没有下载过ffmpeg.exe的，请下载releaseffmpeg.zip。
3.  解压至单独的工作目录，创建`bin`子目录，将ffmpeg.exe放入该子目录，将该目录添加到系统环境的path中。
4.  将 `config/configenv` 改名为 `config/config.env`。
5.  执行 `cnn10vd.exe` 文件，视频文件会下载到当前目录的`video`子目录中。

#### 程序员同学
1.  请至 https://github.com/zhurong2020/cnnvideo-timer 下载源码。
2.  将 `config/configenv` 改名为 `config/config.env` 后进行参数配置。
3.  **设置虚拟环境并安装依赖：**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
4.  各种花式使用，可以实现实时下载，计划下载，下载多个视频，更换其它新闻频道下载，更换下载文件规格，查看youtube视频元数据，上传百度云盘等功能。
5.  运行调度器：`python src/scheduler.py`
6.  欢迎 star、fork 和 pr。

### Mac 和 Linux
1.  确保已安装 Python。
2.  运行以下命令来一键自动部署项目(Ubuntu和Debian)：

    ```bash
    curl -sSL https://raw.githubusercontent.com/zhurong2020/cnnvideo-timer/main/scripts/deploy.sh | bash
    ```

    如果需要手工部署，请确保 `scripts/deploy.sh` 脚本有执行权限。可以使用如下命令进行检查和设置：
    ```bash
    chmod +x scripts/deploy.sh
    ```

## 常见问题
-   Linux 下的安装问题请查看 `docs/FAQ.md` 文档。

## 贡献
如有任何问题或建议，或想要参与项目贡献，可以通过邮件方式联系我们，或在项目中提出 Issue 或 Pull Request。

## 许可证
This project is licensed under the MIT License - see the `docs/LICENSE.md` file for details.

## 风险提示
使用此工具和下载使用视频时，请遵守相关法律法规，以及视频原创者的使用条款和条件，并尊重版权。

## 联系信息
如有任何问题或建议，请发邮件：admin@zhurong.link