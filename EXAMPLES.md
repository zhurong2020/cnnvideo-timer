# Usage Examples

Complete examples for using SmartNews Learn in various scenarios.

---

## Table of Contents

1. [CLI Examples](#cli-examples)
2. [API Examples](#api-examples)
3. [Python SDK Examples](#python-sdk-examples)
4. [WordPress Integration](#wordpress-integration)
5. [Advanced Use Cases](#advanced-use-cases)

---

## CLI Examples

### Basic Download

```bash
# Download latest CNN10 video
python main.py

# Download with custom settings
python main.py --max-videos 3 --output ./downloads
```

### Scheduled Downloads

```bash
# Start scheduler (runs every 12 hours at 8am and 8pm)
python main.py --schedule

# Runs in background until stopped with Ctrl+C
```

### Custom Channel

```bash
# Download from BBC Learning English
python main.py --channel "https://www.youtube.com/@bbclearningenglish/videos"
```

---

## API Examples

### 1. Get Available Sources

**Request:**
```bash
curl http://localhost:8000/api/v1/sources
```

**Response:**
```json
{
  "sources": [
    {
      "id": "cnn10",
      "name": "CNN 10",
      "description": "10-minute daily news for students",
      "url": "https://www.youtube.com/@CNN10/videos",
      "icon": "youtube",
      "min_tier": "free",
      "tags": ["youtube", "news", "english"]
    },
    {
      "id": "bbc_learning",
      "name": "BBC Learning English",
      "description": "English learning videos from BBC",
      "url": "https://www.youtube.com/@bbclearningenglish/videos",
      "icon": "youtube",
      "min_tier": "free",
      "tags": ["youtube", "news", "english"]
    }
  ]
}
```

### 2. Get Latest Videos

**Request:**
```bash
curl "http://localhost:8000/api/v1/sources/cnn10/videos?limit=5"
```

**Response:**
```json
{
  "source_id": "cnn10",
  "videos": [
    {
      "id": "abc123xyz",
      "title": "CNN 10 - December 4, 2024",
      "url": "https://www.youtube.com/watch?v=abc123xyz",
      "thumbnail": "https://i.ytimg.com/vi/abc123xyz/maxresdefault.jpg",
      "duration": 600,
      "upload_date": "20241204",
      "source_id": "cnn10"
    }
  ]
}
```

### 3. Preview Video Info

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/sources/preview \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=abc123xyz"}'
```

**Response:**
```json
{
  "id": "abc123xyz",
  "title": "CNN 10 - December 4, 2024",
  "url": "https://www.youtube.com/watch?v=abc123xyz",
  "thumbnail": "https://i.ytimg.com/vi/abc123xyz/maxresdefault.jpg",
  "duration": 600,
  "upload_date": "20241204"
}
```

### 4. Create Task (Different Modes)

#### Original Video (No Processing)
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user123" \
  -d '{
    "source_id": "cnn10",
    "video_url": "https://www.youtube.com/watch?v=abc123xyz",
    "processing_mode": "original"
  }'
```

#### With AI Subtitle
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user123" \
  -d '{
    "source_id": "cnn10",
    "video_url": "https://www.youtube.com/watch?v=abc123xyz",
    "processing_mode": "with_subtitle"
  }'
```

#### Repeat Twice (Learning Mode)
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user123" \
  -d '{
    "source_id": "cnn10",
    "video_url": "https://www.youtube.com/watch?v=abc123xyz",
    "processing_mode": "repeat_twice"
  }'
```

#### Slow Speed with Subtitle
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user123" \
  -d '{
    "source_id": "cnn10",
    "video_url": "https://www.youtube.com/watch?v=abc123xyz",
    "processing_mode": "slow"
  }'
```

**Response:**
```json
{
  "id": "task-uuid-here",
  "user_id": "user123",
  "source_id": "cnn10",
  "video_id": "abc123xyz",
  "video_url": "https://www.youtube.com/watch?v=abc123xyz",
  "video_title": "CNN 10 - December 4, 2024",
  "status": "pending",
  "processing_mode": "with_subtitle",
  "progress": 0,
  "created_at": "2024-12-05T10:00:00",
  "updated_at": "2024-12-05T10:00:00",
  "completed_at": null,
  "download_url": null,
  "error_message": null
}
```

### 5. Check Task Status

```bash
curl http://localhost:8000/api/v1/tasks/task-uuid-here
```

**Response (In Progress):**
```json
{
  "id": "task-uuid-here",
  "status": "processing",
  "progress": 65,
  "video_title": "CNN 10 - December 4, 2024",
  ...
}
```

**Response (Completed):**
```json
{
  "id": "task-uuid-here",
  "status": "completed",
  "progress": 100,
  "download_url": "/api/v1/tasks/task-uuid-here/download",
  ...
}
```

### 6. List User's Tasks

```bash
# All tasks
curl -H "X-User-Id: user123" \
  http://localhost:8000/api/v1/tasks

# Filter by status
curl -H "X-User-Id: user123" \
  "http://localhost:8000/api/v1/tasks?status=completed&limit=10"
```

### 7. Download Processed Video

```bash
curl -H "X-User-Id: user123" \
  http://localhost:8000/api/v1/tasks/task-uuid-here/download \
  -o video.mp4
```

### 8. Delete Task

```bash
curl -X DELETE \
  -H "X-User-Id: user123" \
  http://localhost:8000/api/v1/tasks/task-uuid-here
```

---

## Python SDK Examples

### Basic Usage

```python
from pathlib import Path
from src.processors import process_video_for_learning

# Simple: Add subtitle to video
process_video_for_learning(
    video_path=Path("input.mp4"),
    output_path=Path("output.mp4"),
    mode="with_subtitle",
    video_url="https://youtube.com/watch?v=abc123",
)
```

### Advanced Usage

```python
from pathlib import Path
from src.core.downloader import VideoDownloader
from src.processors.subtitle import SubtitleGenerator
from src.processors.ffmpeg import FFmpegProcessor

# 1. Download video
downloader = VideoDownloader()
result = downloader.download("https://youtube.com/watch?v=abc123")

if result.success:
    video_path = result.file_path

    # 2. Generate subtitle
    subtitle_gen = SubtitleGenerator(model_size="base", language="en")
    subtitle_path = subtitle_gen.generate_from_video(video_path)

    # 3. Embed subtitle
    ffmpeg = FFmpegProcessor()
    output_path = Path("output_with_subtitle.mp4")
    ffmpeg.embed_subtitle_hard(video_path, subtitle_path, output_path)

    print(f"✓ Done: {output_path}")
```

### Custom Processing Pipeline

```python
from pathlib import Path
from src.processors.ffmpeg import FFmpegProcessor
from src.processors.subtitle import SubtitleGenerator

def create_learning_video(input_video, output_video):
    """Create a learning video: slow speed + large subtitles."""

    ffmpeg = FFmpegProcessor()
    subtitle_gen = SubtitleGenerator(model_size="small")

    # Step 1: Generate subtitle
    print("Generating subtitles...")
    subtitle_path = subtitle_gen.generate_from_video(input_video)

    # Step 2: Slow down video
    print("Slowing video to 0.75x speed...")
    slow_video = Path("temp_slow.mp4")
    ffmpeg.adjust_speed(input_video, slow_video, speed_factor=0.75)

    # Step 3: Add large, readable subtitles
    print("Adding subtitles...")
    ffmpeg.embed_subtitle_hard(
        slow_video,
        subtitle_path,
        output_video,
        subtitle_style={
            'FontSize': 28,
            'PrimaryColour': '&H00FFFF00',  # Cyan
            'OutlineColour': '&H00000000',
            'Alignment': 2,
            'MarginV': 40,
        }
    )

    # Cleanup
    slow_video.unlink()

    print(f"✓ Created learning video: {output_video}")

# Usage
create_learning_video(
    input_video=Path("cnn10.mp4"),
    output_video=Path("cnn10_learning.mp4")
)
```

---

## WordPress Integration

### PHP Functions

```php
<?php
/**
 * SmartNews Learn WordPress Integration
 */

// Config
define('CNNVIDEO_API_URL', 'http://localhost:8000/api/v1');

/**
 * Make API request
 */
function cnnvideo_api_request($endpoint, $method = 'GET', $data = null) {
    $url = CNNVIDEO_API_URL . $endpoint;

    $args = [
        'method' => $method,
        'headers' => [
            'Content-Type' => 'application/json',
            'X-User-Id' => get_current_user_id(),
        ],
        'timeout' => 30,
    ];

    if ($data) {
        $args['body'] = json_encode($data);
    }

    $response = wp_remote_request($url, $args);

    if (is_wp_error($response)) {
        return ['error' => $response->get_error_message()];
    }

    return json_decode(wp_remote_retrieve_body($response), true);
}

/**
 * Get available sources
 */
function cnnvideo_get_sources() {
    return cnnvideo_api_request('/sources');
}

/**
 * Get latest videos from a source
 */
function cnnvideo_get_videos($source_id, $limit = 10) {
    return cnnvideo_api_request("/sources/{$source_id}/videos?limit={$limit}");
}

/**
 * Create download task
 */
function cnnvideo_create_task($video_url, $mode = 'with_subtitle') {
    return cnnvideo_api_request('/tasks', 'POST', [
        'source_id' => 'cnn10',
        'video_url' => $video_url,
        'processing_mode' => $mode,
    ]);
}

/**
 * Get user's tasks
 */
function cnnvideo_get_tasks($status = null) {
    $endpoint = '/tasks';
    if ($status) {
        $endpoint .= "?status={$status}";
    }
    return cnnvideo_api_request($endpoint);
}

/**
 * Get task details
 */
function cnnvideo_get_task($task_id) {
    return cnnvideo_api_request("/tasks/{$task_id}");
}

/**
 * Delete task
 */
function cnnvideo_delete_task($task_id) {
    return cnnvideo_api_request("/tasks/{$task_id}", 'DELETE');
}
?>
```

### Shortcode Example

```php
<?php
/**
 * Shortcode: [cnnvideo_list]
 * Display latest CNN10 videos with download button
 */
function cnnvideo_list_shortcode($atts) {
    $atts = shortcode_atts([
        'source' => 'cnn10',
        'limit' => 5,
        'mode' => 'with_subtitle',
    ], $atts);

    $result = cnnvideo_get_videos($atts['source'], $atts['limit']);

    if (empty($result['videos'])) {
        return '<p>No videos available.</p>';
    }

    ob_start();
    ?>
    <div class="cnnvideo-list">
        <?php foreach ($result['videos'] as $video): ?>
        <div class="cnnvideo-item">
            <h3><?php echo esc_html($video['title']); ?></h3>
            <img src="<?php echo esc_url($video['thumbnail']); ?>" alt="">
            <button class="cnnvideo-download"
                    data-url="<?php echo esc_attr($video['url']); ?>"
                    data-mode="<?php echo esc_attr($atts['mode']); ?>">
                Download with Subtitle
            </button>
        </div>
        <?php endforeach; ?>
    </div>

    <script>
    jQuery(document).ready(function($) {
        $('.cnnvideo-download').click(function() {
            var btn = $(this);
            var url = btn.data('url');
            var mode = btn.data('mode');

            btn.prop('disabled', true).text('Creating task...');

            $.ajax({
                url: '<?php echo admin_url('admin-ajax.php'); ?>',
                method: 'POST',
                data: {
                    action: 'cnnvideo_create_task',
                    video_url: url,
                    mode: mode,
                },
                success: function(response) {
                    if (response.success) {
                        alert('Download started! Task ID: ' + response.data.id);
                        window.location.href = '/my-downloads/';
                    } else {
                        alert('Error: ' + response.data);
                        btn.prop('disabled', false).text('Download with Subtitle');
                    }
                },
            });
        });
    });
    </script>
    <?php
    return ob_get_clean();
}
add_shortcode('cnnvideo_list', 'cnnvideo_list_shortcode');

/**
 * AJAX handler for creating task
 */
function cnnvideo_ajax_create_task() {
    $video_url = $_POST['video_url'];
    $mode = $_POST['mode'];

    $result = cnnvideo_create_task($video_url, $mode);

    if (isset($result['error'])) {
        wp_send_json_error($result['error']);
    } else {
        wp_send_json_success($result);
    }
}
add_action('wp_ajax_cnnvideo_create_task', 'cnnvideo_ajax_create_task');
?>
```

---

## Advanced Use Cases

### Batch Processing

```python
from pathlib import Path
from src.sources.youtube import CNN10Source
from src.processors import process_video_for_learning
import asyncio

async def download_week_videos():
    """Download all videos from the past week."""
    source = CNN10Source()
    videos = await source.get_latest_videos(limit=7)

    for video in videos:
        print(f"Processing: {video.title}")

        # Download and process
        output_path = Path(f"downloads/{video.id}.mp4")
        process_video_for_learning(
            video_path=None,  # Will download
            output_path=output_path,
            mode="with_subtitle",
            video_url=video.url,
        )

asyncio.run(download_week_videos())
```

### Custom Subtitle Style

```python
from pathlib import Path
from src.processors.ffmpeg import FFmpegProcessor
from src.processors.subtitle import SubtitleGenerator

# Generate subtitle
subtitle_gen = SubtitleGenerator()
subtitle_path = subtitle_gen.generate_from_video(Path("video.mp4"))

# Custom style: Large yellow text with black background
ffmpeg = FFmpegProcessor()
ffmpeg.embed_subtitle_hard(
    Path("video.mp4"),
    subtitle_path,
    Path("output.mp4"),
    subtitle_style={
        'FontName': 'Arial Black',
        'FontSize': 32,
        'PrimaryColour': '&H0000FFFF',  # Yellow
        'OutlineColour': '&H00000000',  # Black
        'BackColour': '&H80000000',     # Semi-transparent black background
        'BorderStyle': 3,
        'Outline': 3,
        'Shadow': 2,
        'Alignment': 2,
        'MarginV': 50,
    }
)
```

### Multilingual Support

```python
from src.processors.subtitle import SubtitleGenerator

# Generate English subtitle
en_gen = SubtitleGenerator(language="en")
en_subtitle = en_gen.generate_from_video(Path("video.mp4"))

# You can also try other languages if video contains them
# zh_gen = SubtitleGenerator(language="zh")  # Chinese
# es_gen = SubtitleGenerator(language="es")  # Spanish
```

---

For more examples, check the API documentation at http://localhost:8000/docs
