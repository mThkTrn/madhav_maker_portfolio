<?php
// Load environment variables from .env file if it exists
if (file_exists(__DIR__ . '/.env')) {
    $lines = file(__DIR__ . '/.env', FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos(trim($line), '#') === 0) continue; // Skip comments
        putenv(trim($line));
    }
}

// OpenAI API Configuration - Read from environment variable with fallback
define('OPENAI_API_KEY', getenv('OPENAI_API_KEY') ?: '');

// Set a default timezone
date_default_timezone_set('UTC');

// Enable error reporting for development
ini_set('display_errors', 1);
error_reporting(E_ALL);

// Function to call OpenAI API
function generateRoast($data) {
    $apiKey = OPENAI_API_KEY;
    $endpoint = 'https://api.openai.com/v1/chat/completions';
    
    // Prepare the prompt with user data
    $prompt = "You are a witty, sarcastic college admissions consultant. Roast the following college application:\n\n";
    
    // Add GPA
    $gpa = number_format(floatval($data['gpa']), 2);
    $prompt .= "GPA: {$gpa}/4.0\n";
    
    // Add Major
    $major = $data['major'] ?? 'Undeclared';
    $prompt .= "Intended Major: {$major}\n";
    
    // Add Extracurriculars
    $prompt .= "\nExtracurricular Activities:\n";
    $ecs = $data['ecs'] ?? [];
    foreach ($ecs as $i => $ec) {
        $prompt .= sprintf("%d. %s (%s)\n", 
            $i + 1, 
            $ec['name'],
            $ec['role']
        );
        if (!empty($ec['description'])) {
            $prompt .= "   " . wordwrap($ec['description'], 70, "\n   ") . "\n";
        }
    }
    
    // Add Fun Fact if available
    if (!empty($data['fact'])) {
        $prompt .= "\nFun Fact: " . $data['fact'] . "\n";
    }
    
    $prompt .= "\nProvide a snarky but not mean-spirited roast of this application. Be clever and witty in your assessment.";
    
    // Prepare the API request
    $messages = [
        [
            "role" => "system",
            "content" => "You are the sassiest, most sarcastic college admissions consultant who ever lived. Your roasts should be so sharp they could cut glass, but still make the reader laugh. Format your response as a JSON object with these exact keys:

{
  \"score\": 7,  // Number from 1-10 (be harsh but fair)
  \"tagline\": \"A brutally honest 3-5 word summary\",
  \"blurb\": \"A short, scathingly sarcastic paragraph that would make Oscar Wilde proud. 2-3 sentences max.\",
  \"bullet_points\": [
    \"• First roast about their activities\",
    \"• Second roast on their academics\",
    \"• Third roast about their fun fact\"
  ]
}

Example response (tone we're aiming for):
{
  \"score\": 4,
  \"tagline\": \"Delusion in a Trench Coat\",
  \"blurb\": \"This application reads like someone Googled 'How to get into Harvard' at 2AM and treated the results like a sacred text. It’s giving ‘achievement unlocked’ energy without the actual gameplay.\",
  \"bullet_points\": [
    \"• Your extracurriculars are a cry for help disguised as a Common App list—10 clubs, 0 personality.\",
    \"• Your transcript is a rollercoaster built by someone with commitment issues: impressive peak, sudden drop, occasional nausea.\",
    \"• 'Fun fact: I love sudoku'—the perfect personality trait for someone hoping to be replaced by an Excel macro.\"
  ]
}

Remember: The goal is to make them go 'Ouch... but also, fair.' Be ruthless but not cruel. The more specific the roast, the better. If they don't question all their life choices after reading this, you're not doing it right. For score, like 10 is an IMO gold or ISEF winnner, 0 is a 0 GPA and 4 is an average 3.5 GPA."
        ],
        [
            "role" => "user",
            "content" => $prompt
        ]
    ];
    
    $data = [
        'model' => 'gpt-4.1-nano-2025-04-14',
        'messages' => $messages,
        'temperature' => 0.8,
        'max_tokens' => 1000,
        'response_format' => ['type' => 'json_object']
    ];
    
    $ch = curl_init($endpoint);
    
    // Set cURL options
    $options = [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($data),
        CURLOPT_HTTPHEADER => [
            'Content-Type: application/json',
            'Authorization: Bearer ' . $apiKey
        ],
        // SSL verification settings
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_CAINFO => __DIR__ . '/cacert.pem',
        CURLOPT_TIMEOUT => 30,
        CURLOPT_CONNECTTIMEOUT => 10
    ];
    
    // Apply all options
    curl_setopt_array($ch, $options);
    
    // For Windows, try to find the CA bundle if the file doesn't exist
    if (!file_exists($options[CURLOPT_CAINFO]) && strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
        // Try to use the system's CA store
        if (file_exists('C:\Windows\System32\curl-ca-bundle.crt')) {
            curl_setopt($ch, CURLOPT_CAINFO, 'C:\\Windows\\System32\\curl-ca-bundle.crt');
        } else {
            // As a last resort, disable SSL verification (not recommended for production)
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
            curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
            error_log('Warning: SSL verification disabled - using insecure connection');
        }
    }
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    
    if (curl_errno($ch)) {
        return ['error' => 'API request failed: ' . curl_error($ch)];
    }
    
    curl_close($ch);
    
    if ($httpCode !== 200) {
        return ['error' => 'API request failed with status code ' . $httpCode . ': ' . $response];
    }
    
    $result = json_decode($response, true);
    
    if (isset($result['choices'][0]['message']['content'])) {
        $content = $result['choices'][0]['message']['content'];
        $roastData = json_decode($content, true);
        
        // Validate the response structure
        if (json_last_error() !== JSON_ERROR_NONE) {
            return ['error' => 'Invalid JSON response from API'];
        }
        
        return $roastData;
    }
    
    return ['error' => 'Unexpected API response format'];
}
?>
