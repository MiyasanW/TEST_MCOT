
import os

content = """{% extends 'unfold/layouts/base.html' %}
{% load humanize %}
{% load inventory_extras %}

{% block content %}
<div class="p-4 md:p-8 space-y-8 font-sans">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <div class="flex items-center gap-3">
                <a href="/admin/" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
                    </svg>
                </a>
                <h1 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Inventory Dashboard</h1>
            </div>
            <p class="text-gray-500 dark:text-gray-400 mt-1 text-base ml-9">Availability for <span class="font-bold text-primary-600 dark:text-primary-400">{{ pretty_date }}</span></p>
        </div>

        <form method="get" class="flex items-center gap-3 bg-white dark:bg-gray-800 p-2 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
            <label for="date" class="text-sm font-medium text-gray-700 dark:text-gray-300 pl-2">Date:</label>
            <input type="date" name="date" id="date" value="{{ selected_date }}" onchange="this.form.submit()" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
        </form>
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
            <table class="w-full text-left text-sm text-gray-500 dark:text-gray-400">
                <thead class="bg-gray-50 dark:bg-gray-700/50 text-xs uppercase text-gray-700 dark:text-gray-300 font-semibold tracking-wider">
                    <tr>
                        <th class="px-6 py-4">Product</th>
                        <th class="px-6 py-4 text-center">Total Stock</th>
                        <th class="px-6 py-4 text-center">Available</th>
                        <th class="px-6 py-4 text-center">Status</th>
                        <th class="px-6 py-4">Recent Logs</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
                    {% for item in inventory %}
                    <tr class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition cursor-pointer" onclick="document.getElementById('log-{{ item.product.id }}').classList.toggle('hidden')">
                        <td class="px-6 py-4 font-medium text-gray-900 dark:text-white">
                            <div class="flex items-center gap-3">
                                {% if item.product.image %}
                                <img src="{{ item.product.image.url }}" class="w-10 h-10 rounded-lg object-cover bg-gray-100">
                                {% else %}
                                <div class="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                                    <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                    </svg>
                                </div>
                                {% endif %}
                                <div>
                                    <div class="font-bold">{{ item.product.name }}</div>
                                    <div class="text-xs text-gray-500 uppercase">{{ item.product.category }}</div>
                                </div>
                            </div>
                        </td>
                        <td class="px-6 py-4 text-center font-mono font-bold text-gray-900 dark:text-white">{{ item.total_stock }}</td>
                        <td class="px-6 py-4 text-center">
                            <span class="px-2.5 py-1 rounded-full text-xs font-bold {% if item.available_stock > 0 %}bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300{% else %}bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300{% endif %}">
                                {{ item.available_stock }}
                            </span>
                        </td>
                        <td class="px-6 py-4 text-center">
                            {% if item.available_stock == 0 %}
                            <span class="text-red-500 text-xs font-semibold">Out of Stock</span>
                            {% elif item.available_stock < 3 %}
                            <span class="text-yellow-500 text-xs font-semibold">Low Stock</span>
                            {% else %}
                            <span class="text-green-500 text-xs font-semibold">Good</span>
                            {% endif %}
                        </td>
                        <td class="px-6 py-4 text-xs">
                            <span class="text-primary-600 hover:underline">View History &darr;</span>
                        </td>
                    </tr>
                    <tr id="log-{{ item.product.id }}" class="hidden bg-gray-50/50 dark:bg-gray-800/50">
                        <td colspan="5" class="px-6 py-4">
                            <div class="space-y-4">
                                <h4 class="text-xs font-bold uppercase tracking-wider text-gray-500">Transaction Ledger <!-- FILE_VERIFY_ID: CHECK_NUCLEAR_FIX --></h4>
                                {% if item.ledger %}
                                <div class="relative border-l-2 border-gray-200 dark:border-gray-700 ml-2 space-y-4">
                                    {% for entry in item.ledger %}
                                    <div class="ml-4 flex items-start gap-4">
                                        <div class="min-w-[80px] text-xs text-gray-400 pt-1">{{ entry.entry_title }}</div>
                                        <div class="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-100 dark:border-gray-700 shadow-sm flex-1">
                                            <div class="flex justify-between items-start">
                                                <div>
                                                    <span class="font-bold text-gray-900 dark:text-white">{{ entry.date_display }}</span>
                                                    {% if entry.package_name %}
                                                    <span class="block text-xs text-purple-600 font-medium mt-0.5">Note: Part of {{ entry.package_name }}</span>
                                                    {% endif %}
                                                </div>
                                                <span class="font-mono font-bold text-red-600">{{ entry.change }}</span>
                                            </div>
                                            <p class="text-xs text-gray-600 dark:text-gray-300 mt-1">{{ entry.detail }}</p>
                                        </div>
                                    </div>
                                    {% endfor %}
                                </div>
                                {% else %}
                                <p class="text-xs text-gray-400 italic">No recent transactions found.</p>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
"""

with open('templates/admin/inventory_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully overwrote templates/admin/inventory_dashboard.html with {len(content)} bytes.")
