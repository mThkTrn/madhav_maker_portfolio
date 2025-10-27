<?php
// Start session and include config
session_start();
require_once 'config.php';

// Initialize variables
$results = [];
$score = 0;
$scoreClass = 'text-gray-700';
$showResults = false;

// Process form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get form data
    $gpa = floatval($_POST['gpa'] ?? 0);
    $major = trim($_POST['major'] ?? '');
    $fact = trim($_POST['fact'] ?? '');
    $ecs = json_decode($_POST['ecs'] ?? '[]', true);
    
    // Prepare data for OpenAI
    $data = [
        'gpa' => $gpa,
        'major' => $major,
        'fact' => $fact,
        'ecs' => $ecs
    ];
    
    // Generate roast using OpenAI
    $roastData = null;
    $useFallback = false;
    
    try {
        $roastData = generateRoast([
            'gpa' => $gpa,
            'major' => $major,
            'fact' => $fact,
            'ecs' => $ecs
        ]);
        
        // Debug: Log the input data and response
        error_log("=== DEBUG: Input Data ===\n" . print_r([
            'gpa' => $gpa,
            'major' => $major,
            'fact' => $fact,
            'ecs' => $ecs,
            'ecs_json' => json_encode($ecs, JSON_PRETTY_PRINT)
        ], true));
        
        if (isset($roastData['error'])) {
            error_log("OpenAI API Error: " . $roastData['error']);
            $useFallback = true;
        }
    } catch (Exception $e) {
        error_log("OpenAI API Error: " . $e->getMessage());
        $useFallback = true;
    }
    
    if ($roastData && !isset($roastData['error'])) {
        // Use OpenAI response with new format
        $results = [
            'title' => $roastData['tagline'] ?? 'Your Roast',
            'score' => $roastData['score'] ?? 5,
            'roasts' => $roastData['bullet_points'] ?? [],
            'verdict' => $roastData['blurb'] ?? 'No verdict generated.'
        ];
    } else {
        // Fallback to algorithmic critique
        $useFallback = true;
    }
    
    if ($useFallback) {
        // Generate algorithmic critique
        $score = 0;
        $roasts = [];
        
        // Base score on GPA (0-6 points)
        if ($gpa >= 3.8) {
            $score += 6;
            $roasts[] = "A 3.8+ GPA? Sure it's not photoshopped?";
        } elseif ($gpa >= 3.5) {
            $score += 4;
            $roasts[] = "3.5+ GPA - Did you sleep in high school? Oh wait, you probably didn't.";
        } elseif ($gpa >= 3.0) {
            $score += 3;
            $roasts[] = "{3.0 GPA} - Perfectly average. How... inspiring.";
        } else {
            $score += 1;
            $roasts[] = "{GPA} - Did you try turning it off and on again?";
        }
        
        // Evaluate activities (0-4 points)
        $ecCount = count($data['ecs']);
        if ($ecCount === 0) {
            $roasts[] = "No activities? Did you leave your house in high school?";
        } else {
            $score += min(4, $ecCount);
            if ($ecCount > 5) {
                $roasts[] = "{$ecCount} activities? When did you find time to breathe?";
            }
            
            // Check for leadership roles
            $hasLeadership = false;
            $activityNames = [];
            foreach ($data['ecs'] as $ec) {
                $activityNames[] = $ec['name'];
                if (in_array(strtolower($ec['role']), ['president', 'captain', 'founder', 'leader'])) {
                    $hasLeadership = true;
                }
            }
            
            if ($hasLeadership) {
                $score += 2;
                $roasts[] = "Leadership role? More like 'listed on resume' role.";
            }
            
            $activityList = implode(', ', array_slice($activityNames, 0, 3));
            if (count($activityNames) > 3) {
                $roasts[] = "3.0 GPA - Perfectly average. How... inspiring.";
            } else {
                $roasts[] = "<3.0 GPA - Did you try... studying?";
            }
            
            // Major (0-3 points)
            $majorLower = strtolower($major);
            if (strpos($majorLower, 'computer') !== false || strpos($majorLower, 'cs') !== false) {
                $score += 3;
                $roasts[] = "CS Major - Oh, another one. How original.";
            } elseif (strpos($majorLower, 'business') !== false) {
                $score += 2;
                $roasts[] = "Business Major - So you want to be rich but don't know how to code?";
            } else {
                $score += 1;
                $roasts[] = "$major? Cute. Hope you like academia.";
            }
            
            // Activities (0-3 points)
            if (!empty($ecs)) {
                $ecCount = count($ecs);
                $score += min(3, $ecCount);
                $roasts[] = "$ecCount activities? That's it?";
            } else {
                $roasts[] = "No activities? Did you even leave your room in high school?";
            }
        }
        
        // Fun fact analysis
        $fact = strtolower($data['fact']);
        if (strlen($fact) > 0) {
            if (strlen($fact) < 10) {
                $roasts[] = "That's your fun fact? Did you run out of creativity?";
            } elseif (strpos($fact, '!') !== false) {
                $roasts[] = "Someone's excited about their fun fact. Calm down.";
            } else {
                $roasts[] = "Fun fact? More like 'fun'try.";
            }
        } else {
            $roasts[] = "No fun fact? Guess you're not that fun.";
        }
        
        // Cap score at 10
        $score = min(10, $score);
        
        // Generate title based on score
        if ($score >= 8) {
            $title = "Overachiever Alert";
        } elseif ($score >= 5) {
            $title = "Perfectly Average";
        } else {
            $title = "Community College Material";
        }
        
        $results = [
            'title' => $title,
            'score' => $score,
            'roasts' => $roasts,
            'verdict' => $score >= 8 ? "Not bad... for a tryhard." : 
                         ($score >= 5 ? "You exist, I guess." : "Did you even try?")
        ];
    }
    
    // Set score class based on score
    $score = $results['score'];
    if ($score >= 8) $scoreClass = 'text-green-600';
    elseif ($score >= 5) $scoreClass = 'text-yellow-600';
    else $scoreClass = 'text-red-600';
    
    $showResults = true;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Crack My App - Roast</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
  <style>
    body { font-family: Helvetica, Arial, sans-serif; }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    
    .loading {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 2rem;
    }
    
    .spinner {
      width: 50px;
      height: 50px;
      border: 5px solid #f3f3f3;
      border-top: 5px solid #8b5cf6;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 1rem;
    }
    
    .roast-item {
      opacity: 0;
      transform: translateY(10px);
      animation: fadeIn 0.3s ease-out forwards;
    }
    
    @keyframes fadeIn {
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    .ec-card {
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 0.75rem;
      padding: 1.25rem;
      margin-bottom: 1.25rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      transition: all 0.2s ease;
    }
    
    .ec-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
    }
    
    .ec-card:last-child {
      margin-bottom: 0;
    }
    
    .ec-role {
      appearance: none;
      background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
      background-position: right 0.5rem center;
      background-repeat: no-repeat;
      background-size: 1.5em 1.5em;
      padding-right: 2.5rem;
    }
  </style>
</head>
<body class="bg-gradient-to-br from-purple-600 to-pink-400 min-h-screen flex items-center justify-center p-4">
  <div class="bg-white bg-opacity-90 backdrop-blur-md p-6 rounded-2xl shadow-lg w-full max-w-lg">
    <?php if ($showResults): ?>
      <!-- Results View -->
      <div id="results" class="animate-fade-in">
        <h2 class="text-2xl font-bold text-center mb-4">Your Roasted Score</h2>
        <div id="result-card" class="bg-gray-100 p-6 rounded-2xl shadow-inner">
          <h3 class="text-center text-lg font-semibold mb-3 text-gray-700">
            🧠 Personality: <span id="archetype" class="italic text-gray-800"><?= htmlspecialchars($results['title']) ?></span>
          </h3>
          <p id="final-score" class="text-4xl font-bold text-center mb-4 <?= $scoreClass ?>">
            <?= $score ?>/10
          </p>
          
          <div class="space-y-4">
            <?php if (!empty($results['verdict'])): ?>
              <p class="text-gray-800"><?= nl2br(htmlspecialchars($results['verdict'])) ?></p>
            <?php endif; ?>
            
            <?php if (!empty($results['roasts'])): ?>
              <ul class="list-disc list-inside text-gray-800 space-y-3">
            <?php 
            $delay = 0.1;
            foreach ($results['roasts'] as $index => $roast): 
              $delay += 0.1;
            ?>
              <li class="roast-item" style="animation-delay: <?= $delay ?>s">
                <?= htmlspecialchars($roast) ?>
                <?php if (strlen($roast) < 30): ?>
                  <span class="text-red-500">🔥</span>
                <?php endif; ?>
              </li>
            <?php endforeach; ?>
          </ul>
            <?php endif; ?>
          </div>
        </div>
        
        <div class="flex justify-center mt-4">
          <button id="share-score" class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Share My Score</button>
        </div>
      </div>
    <?php else: ?>
      <!-- Multi-step Form -->
      <div id="step-container">
        <!-- Step 0: Intro -->
        <div class="step" id="step-0">
          <h1 class="text-4xl font-extrabold text-center mb-4">Crack My App</h1>
          <p class="text-center italic mb-6">Get your college app roasted by AI in seconds.</p>
          <button id="start" class="w-full py-3 bg-red-600 text-white rounded-md hover:bg-red-700">
            Start Roast →
          </button>
        </div>
        
        <!-- Step 1: Activities -->
        <div class="step hidden" id="step-1">
          <h2 class="text-2xl font-bold text-center mb-4">Step 1: Your Activities</h2>
          <div id="ecs-list" class="space-y-4"></div>
          <button id="add-ec" class="mt-2 text-blue-600 hover:underline">+ Add another activity</button>
          <div class="flex justify-between mt-6">
            <button id="back-1" class="px-4 py-2 bg-gray-300 rounded-md">← Back</button>
            <button id="next-1" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Next →</button>
          </div>
        </div>
        
        <!-- Step 2: GPA -->
        <div class="step hidden" id="step-2">
          <h2 class="text-2xl font-bold text-center mb-4">Step 2: GPA</h2>
          <input type="number" id="gpa-input" step="0.01" min="0" max="4" placeholder="e.g. 3.85" class="w-full p-2 border rounded-md mb-6" />
          <div class="flex justify-between">
            <button id="back-2" class="px-4 py-2 bg-gray-300 rounded-md">← Back</button>
            <button id="next-2" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Next →</button>
          </div>
        </div>
        
        <!-- Step 3: Major -->
        <div class="step hidden" id="step-3">
          <h2 class="text-2xl font-bold text-center mb-4">Step 3: Intended Major</h2>
          <input list="major-list" id="major-input" class="w-full p-2 border rounded-md mb-6" placeholder="Select or type Major" />
          <datalist id="major-list">
            <option>Computer Science</option><option>Biology</option><option>Economics</option>
            <option>Physics</option><option>Linguistics</option><option>Mathematics</option>
            <option>Chemistry</option><option>Psychology</option><option>Political Science</option>
            <option>History</option><option>English</option><option>Engineering</option>
            <option>Environmental Science</option><option>Music</option><option>Art</option>
            <option>Philosophy</option><option>Sociology</option><option>Other</option>
          </datalist>
          <div class="flex justify-between">
            <button id="back-3" class="px-4 py-2 bg-gray-300 rounded-md">← Back</button>
            <button id="next-3" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Next →</button>
          </div>
        </div>
        
        <!-- Step 4: Fun Fact -->
        <div class="step hidden" id="step-4">
          <h2 class="text-2xl font-bold text-center mb-4">Step 4: Fun Fact</h2>
          <input type="text" id="fact-input" placeholder="e.g. Built a robot that folds laundry" class="w-full p-2 border rounded-md mb-6" />
          <div class="flex justify-between">
            <button id="back-4" class="px-4 py-2 bg-gray-300 rounded-md">← Back</button>
            <button id="next-4" class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">Get Roast →</button>
          </div>
        </div>
      </div>
      
      <!-- Hidden form for submission -->
      <form id="app-form" method="POST" class="hidden">
        <input type="hidden" name="gpa" id="form-gpa">
        <input type="hidden" name="major" id="form-major">
        <input type="hidden" name="fact" id="form-fact">
        <input type="hidden" name="ecs" id="form-ecs">
      </form>
    <?php endif; ?>
    
    <footer class="mt-6 text-center text-sm text-gray-500">Made with ❤️ by Madhavendra Thakur</footer>
  </div>

  <script>
    // Form navigation
    const steps = [...document.querySelectorAll('.step')];
    const show = i => steps.forEach((s,j) => j === i ? s.classList.remove('hidden') : s.classList.add('hidden'));
    
    // Initialize first step
    show(0);

    // EC card functionality
    const ecsList = document.getElementById('ecs-list');
    
    function addEc() {
      if (!ecsList) return; // Exit if we're on the results page
      
      const div = document.createElement('div');
      div.className = 'ec-card bg-gray-50 border p-4 rounded-md mb-3';
      div.innerHTML = `
        <div class="space-y-2">
          <div class="flex flex-wrap gap-2 items-center">
            <input type="text" class="ec-name flex-1 p-2 border rounded-md" placeholder="Activity name" required />
            <select class="ec-role p-2 border rounded-md">
              <option>Member</option>
              <option>Leader</option>
              <option>President</option>
              <option>Vice President</option>
              <option>Captain</option>
              <option>Founder</option>
            </select>
            <button type="button" class="remove-ec px-3 text-red-500 hover:text-red-700">
              ×
            </button>
          </div>
          <textarea class="ec-description w-full p-2 border rounded-md text-sm" 
                    placeholder="Describe your role and achievements (optional)" 
                    rows="2"></textarea>
        </div>`;
        
      // Add remove functionality
      const removeBtn = div.querySelector('.remove-ec');
      if (removeBtn) {
        removeBtn.onclick = () => {
          const cards = document.querySelectorAll('.ec-card');
          if (cards.length > 1) {
            div.remove();
          } else {
            alert('You need at least one activity');
          }
        };
      }
      
      ecsList.appendChild(div);
    }
    
    // Initialize first EC field
    document.addEventListener('DOMContentLoaded', () => {
      if (document.getElementById('ecs-list')) {
        addEc();
        document.getElementById('add-ec').onclick = e => {
          e.preventDefault();
          addEc();
        };
      }
      
      // Start button
      document.getElementById('start')?.addEventListener('click', () => show(1));
      
      // Navigation buttons
      document.getElementById('back-1')?.addEventListener('click', () => show(0));
      document.getElementById('back-2')?.addEventListener('click', () => show(1));
      document.getElementById('back-3')?.addEventListener('click', () => show(2));
      document.getElementById('back-4')?.addEventListener('click', () => show(3));
      
      // Next buttons with validation
      document.getElementById('next-1')?.addEventListener('click', () => {
        const names = [...document.querySelectorAll('.ec-name')].map(i => i.value.trim());
        if (names.some(n => !n)) {
          alert('Please fill out all activities');
          return;
        }
        show(2);
      });
      
      document.getElementById('next-2')?.addEventListener('click', () => {
        const gpa = parseFloat(document.getElementById('gpa-input')?.value);
        if (isNaN(gpa) || gpa < 0 || gpa > 4) {
          alert('Please enter a valid GPA between 0 and 4');
          return;
        }
        show(3);
      });
      
      document.getElementById('next-3')?.addEventListener('click', () => {
        const major = document.getElementById('major-input')?.value.trim();
        if (!major) {
          alert('Please enter your intended major');
          return;
        }
        show(4);
      });
      
      // Show loading screen
      function showLoadingScreen() {
        const loadingHTML = `
          <div class="loading">
            <div class="spinner"></div>
            <h2 class="text-xl font-bold mb-2">Generating Your Roast</h2>
            <p class="text-gray-600">Our AI is preparing to absolutely demolish your college app...</p>
            <p class="text-sm text-gray-500 mt-4">This might take a moment. Try not to cry.</p>
          </div>
        `;
        document.getElementById('step-container').innerHTML = loadingHTML;
      }
      
      // Submit form
      document.getElementById('next-4')?.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Get form values
        const gpa = parseFloat(document.getElementById('gpa-input')?.value);
        const major = document.getElementById('major-input')?.value.trim();
        const fact = document.getElementById('fact-input')?.value.trim() || '';
        
        // Validate form
        if (isNaN(gpa) || gpa < 0 || gpa > 4) {
          alert('Please enter a valid GPA between 0 and 4');
          return;
        }
        
        if (!major) {
          alert('Please enter your intended major');
          return;
        }
        
        // Collect EC data (limit to 5 activities, 150 chars each)
        const ecs = [];
        Array.from(document.querySelectorAll('.ec-card')).slice(0, 5).forEach(card => {
          const name = card.querySelector('.ec-name').value.trim();
          if (name) {  // Only include if name is not empty
            let description = card.querySelector('.ec-description').value.trim();
            if (description.length > 150) {
              description = description.substring(0, 147) + '...';
            }
            ecs.push({
              name: name,
              role: card.querySelector('.ec-role').value,
              description: description
            });
          }
        });
        
        if (ecs.length === 0) {
          alert('Please add at least one activity');
          return;
        }
        
        console.log('Activities being submitted:', ecs);
        
        // Remove existing form if it exists and is a child of body
        let form = document.getElementById('app-form');
        if (form && form.parentNode === document.body) {
          document.body.removeChild(form);
        }
        
        form = document.createElement('form');
        form.id = 'app-form';
        form.method = 'POST';
        form.style.display = 'none';
        document.body.appendChild(form);
        
        // Add form fields with values
        const addField = (name, value) => {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = name;
          input.value = value;
          form.appendChild(input);
        };
        
        addField('gpa', gpa);
        addField('major', major);
        addField('fact', fact);
        addField('ecs', JSON.stringify(ecs));
        
        // Show loading screen
        showLoadingScreen();
        
        // Small delay to ensure loading screen shows
        setTimeout(() => {
          form.submit();
        }, 100);
      });
      
      // Share score
      document.getElementById('share-score')?.addEventListener('click', async () => {
        try {
          const title = document.getElementById('archetype')?.textContent || 'My College App Roast';
          const score = document.getElementById('final-score')?.textContent || '0/10';
          const url = window.location.href.split('?')[0]; // Get current URL without query params
          
          const shareText = `I did this quiz ${url} and I got "${title}", ${score}. Try it yourself!`;
          
          await navigator.clipboard.writeText(shareText);
          alert('Score copied to clipboard!');
        } catch (err) {
          console.error('Error sharing:', err);
          alert('Failed to copy to clipboard');
        }
      });
      
      // Start over
      document.getElementById('start-over')?.addEventListener('click', () => {
        window.location.href = window.location.pathname;
      });
    });
  </script>
</body>
</html>
