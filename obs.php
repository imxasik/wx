<?php 
require_once 'hp/security.php';

// FTP configuration
$ftp_host = 'ftpupload.net';
$ftp_username = 'epiz_32144154';
$ftp_password = 'Im80K123';
$ftp_directory = 'htdocs/data'; // FTP directory to store the file

$source_url = "https://www.ogimet.com/display_synopsc2.php?lang=en&estado=Bang";

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $source_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 15);
curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0');
$html = curl_exec($ch);

if (curl_errno($ch)) {
    die("Error fetching data from the URL: " . curl_error($ch));
}
curl_close($ch);

$lines = explode("\n", $html);
$grouped_data = [];
$current_station = null;
$current_weather_data = [];
$collecting = false;

foreach ($lines as $line) {
    $line = trim($line);
    if (empty($line)) continue;

    // Station header
    if (preg_match('/^#\s*SYNOPS from (\d+), ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^m]+) m/', $line, $matches)) {
        $current_station = [
            'wmo_id' => $matches[1],
            'station_name' => trim($matches[2]),
            'latitude' => $matches[3],
            'longitude' => $matches[4],
            'elevation' => trim($matches[5]),
        ];
        continue;
    }

    // Start of SYNOP report
    if (preg_match('/^(\d{8})(\d{4})\s+AAXX/', $line, $matches)) {
        if ($collecting && $current_station && !empty($current_weather_data)) {
            // Save previous report
            $weather_data = implode(' ', $current_weather_data);
            $date = substr($matches_prev[1], 0, 4) . '-' . substr($matches_prev[1], 4, 2) . '-' . substr($matches_prev[1], 6, 2);
            $time = substr($matches_prev[2], 0, 2) . ':' . substr($matches_prev[2], 2, 2) . 'Z';
            $observation_time = $date . '_' . substr($matches_prev[2], 0, 2) . 'Z';
            $grouped_data[$observation_time][] = [
                'datetime' => $date . ' ' . $time,
                'wmo_id' => $current_station['wmo_id'],
                'station_name' => $current_station['station_name'],
                'latitude' => $current_station['latitude'],
                'longitude' => $current_station['longitude'],
                'elevation' => $current_station['elevation'],
                'weather_data' => $weather_data,
            ];
        }
        // Start new report
        $current_weather_data = [trim(substr($line, 18))];
        $matches_prev = $matches;
        $collecting = true;
        continue;
    }

    // Continuation lines (e.g., 333 section)
    if ($collecting && preg_match('/^\d{3}\s+/', $line)) {
        $current_weather_data[] = trim(preg_replace('/^\d{3}\s+/', '', $line));
        continue;
    }

    // End of report
    if ($collecting && preg_match('/=$/', $line)) {
        $current_weather_data[] = trim(preg_replace('/=$/', '', $line));
        $weather_data = implode(' ', $current_weather_data);
        if ($current_station) {
            $date = substr($matches_prev[1], 0, 4) . '-' . substr($matches_prev[1], 4, 2) . '-' . substr($matches_prev[1], 6, 2);
            $time = substr($matches_prev[2], 0, 2) . ':' . substr($matches_prev[2], 2, 2) . 'Z';
            $observation_time = $date . '_' . substr($matches_prev[2], 0, 2) . 'Z';
            $grouped_data[$observation_time][] = [
                'datetime' => $date . ' ' . $time,
                'wmo_id' => $current_station['wmo_id'],
                'station_name' => $current_station['station_name'],
                'latitude' => $current_station['latitude'],
                'longitude' => $current_station['longitude'],
                'elevation' => $current_station['elevation'],
                'weather_data' => $weather_data,
            ];
        }
        $collecting = false;
        $current_weather_data = [];
        continue;
    }
}

// Save last report if exists
if ($collecting && $current_station && !empty($current_weather_data)) {
    $weather_data = implode(' ', $current_weather_data);
    $date = substr($matches_prev[1], 0, 4) . '-' . substr($matches_prev[1], 4, 2) . '-' . substr($matches_prev[1], 6, 2);
    $time = substr($matches_prev[2], 0, 2) . ':' . substr($matches_prev[2], 2, 2) . 'Z';
    $observation_time = $date . '_' . substr($matches_prev[2], 0, 2) . 'Z';
    $grouped_data[$observation_time][] = [
        'datetime' => $date . ' ' . $time,
        'wmo_id' => $current_station['wmo_id'],
        'station_name' => $current_station['station_name'],
        'latitude' => $current_station['latitude'],
        'longitude' => $current_station['longitude'],
        'elevation' => $current_station['elevation'],
        'weather_data' => $weather_data,
    ];
}

// Find the latest observation time
$latest_observation = null;
$latest_timestamp = 0;

foreach ($grouped_data as $observation_time => $entries) {
    // Convert observation time to timestamp for comparison
    $date_time = str_replace('_', ' ', $observation_time);
    $timestamp = strtotime($date_time);
    if ($timestamp > $latest_timestamp) {
        $latest_timestamp = $timestamp;
        $latest_observation = $observation_time;
    }
}

// Save and upload only the latest data via FTP
if ($latest_observation && isset($grouped_data[$latest_observation])) {
    // Prepare JSON data as a string buffer
    $json_data = json_encode($grouped_data[$latest_observation], JSON_PRETTY_PRINT);

    // Create a memory stream for the JSON data
    $stream = fopen('php://memory', 'r+');
    fwrite($stream, $json_data);
    fseek($stream, 0);

    // Connect to FTP server
    $ftp_connection = ftp_connect($ftp_host);
    if ($ftp_connection === false) {
        fclose($stream);
        die("Failed to connect to FTP server: $ftp_host");
    }

    // Login to FTP server
    if (!ftp_login($ftp_connection, $ftp_username, $ftp_password)) {
        fclose($stream);
        ftp_close($ftp_connection);
        die("FTP login failed");
    }

    // Change to the desired directory
    if (!ftp_chdir($ftp_connection, $ftp_directory)) {
        fclose($stream);
        ftp_close($ftp_connection);
        die("Failed to change to FTP directory: $ftp_directory");
    }

    // Upload file with observation time as filename (e.g., 2025-05-12_12Z.json)
    $remote_filename = $latest_observation . '.json';
    if (!ftp_fput($ftp_connection, $remote_filename, $stream, FTP_BINARY)) {
        fclose($stream);
        ftp_close($ftp_connection);
        die("Failed to upload file to FTP server");
    }

    // Clean up
    fclose($stream);
    ftp_close($ftp_connection);

    echo "Successfully uploaded $remote_filename to FTP server";
}
?>
