<?php
$page_title = "Community Guidelines - Vaach";
include "header.php";
?>

<main class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-5 border-b border-gray-200 bg-white">
                <h1 class="text-2xl font-bold text-gray-900">Community Guidelines</h1>
                <p class="mt-1 text-sm text-gray-500">Last updated: <?php echo date('F j, Y'); ?></p>
            </div>
            
            <div class="px-6 py-6 space-y-8 text-gray-700">
                <section class="bg-blue-50 p-4 rounded-lg">
                    <h2 class="text-xl font-semibold mb-3 text-blue-800">Our Mission</h2>
                    <p class="text-blue-700">Vaach is dedicated to preserving and sharing the world's languages and cultures. We strive to create a respectful, inclusive community where everyone can contribute to language preservation.</p>
                </section>

                <section>
                    <h2 class="text-xl font-semibold mb-3">1. Be Respectful</h2>
                    <p class="mb-4">Treat all community members with respect. We welcome diverse perspectives and encourage constructive discussions about language and culture.</p>
                </section>

                <section>
                    <h2 class="text-xl font-semibold mb-3">2. Content Standards</h2>
                    <p class="mb-2">When contributing content, please ensure it is:</p>
                    <ul class="list-disc pl-5 mb-4 space-y-1">
                        <li><strong>Accurate:</strong> Provide correct translations and information</li>
                        <li><strong>Relevant:</strong> Stay on topic and appropriate for the language being documented</li>
                        <li><strong>Respectful:</strong> Avoid offensive, discriminatory, or harmful content</li>
                        <li><strong>Original:</strong> Only submit content you have the right to share</li>
                    </ul>
                </section>

                <section>
                    <h2 class="text-xl font-semibold mb-3">3. Prohibited Content</h2>
                    <p class="mb-2">The following content is not allowed:</p>
                    <ul class="list-disc pl-5 mb-4 space-y-1">
                        <li>Hate speech or discrimination</li>
                        <li>Harassment or bullying</li>
                        <li>Spam or advertising</li>
                        <li>Copyrighted material without permission</li>
                        <li>False or misleading information</li>
                    </ul>
                </section>

                <section>
                    <h2 class="text-xl font-semibold mb-3">4. Collaboration</h2>
                    <p class="mb-4">We encourage collaboration and peer review. If you see an error, please correct it respectfully. If you disagree with a change, discuss it constructively.</p>
                </section>

                <section>
                    <h2 class="text-xl font-semibold mb-3">5. Attribution</h2>
                    <p class="mb-4">Always give proper credit when using others' contributions. Respect the Creative Commons Attribution-ShareAlike 4.0 International License that governs content on this platform.</p>
                </section>

                <section>
                    <h2 class="text-xl font-semibold mb-3">6. Reporting Issues</h2>
                    <p class="mb-2">If you encounter content that violates these guidelines, please report it to our moderation team. Include:</p>
                    <ul class="list-disc pl-5 mb-4 space-y-1">
                        <li>The specific content in question</li>
                        <li>Why you believe it violates our guidelines</li>
                        <li>Any relevant context</li>
                    </ul>
                </section>

                <section class="bg-yellow-50 p-4 rounded-lg">
                    <h2 class="text-xl font-semibold mb-3 text-yellow-800">Consequences of Violation</h2>
                    <p class="text-yellow-700">Violations of these guidelines may result in content removal, account warnings, or account suspension, depending on the severity and frequency of the violation.</p>
                </section>

                <section>
                    <h2 class="text-xl font-semibold mb-3">Contact Us</h2>
                    <p>If you have questions about these guidelines, please contact us at <a href="mailto:community@vaach.org" class="text-blue-600 hover:underline">community@vaach.org</a>.</p>
                </section>
            </div>
        </div>
    </div>
</main>

<?php include "footer.php"; ?>
