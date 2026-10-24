<div align="center">

# NEXUS-RE

### منصة الذكاء الاصطناعي للهندسة العكسية وتحليل الأمان

*ربط نماذج اللغة الكبيرة (LLMs) بأدوات الهندسة العكسية الاحترافية — عبر Model Context Protocol.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-2.3.0-6C63FF?style=for-the-badge)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-00FF88?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-27%2F27-success?style=for-the-badge)]()

</div>

---

## ما هو NEXUS-RE؟

**NEXUS-RE** منصة مفتوحة المصدر تُمكّن وكلاء الذكاء الاصطناعي من إجراء **هندسة عكسية شاملة** على الملفات التنفيذية والتطبيقات — بدون الحاجة إلى الكود المصدري.

تُوفّر المنصة **31 أداة تحليل ثنائي** عبر **Model Context Protocol (MCP)**، وتُنسّقها عبر **نظام متعدد الوكلاء** (Static، Security، Crypto، Report). كل نتيجة تأتي مع **أدلة، ومستوى ثقة، وقابلية تتبّع كاملة** — مما يجعل الهندسة العكسية **قابلة للتدقيق، وقابلة للتكرار، وموثوقة**.

---

## المشكلة

الهندسة العكسية التقليدية تتطلّب خبرة عالية وتستغرق وقتًا طويلًا:

1. تحميل الملف التنفيذي في Ghidra أو IDA Pro أو radare2.
2. التنقّل اليدوي بين آلاف الدوال.
3. إعادة بناء هياكل البيانات من الذاكرة الخام.
4. الربط بين الأدوات المختلفة (Frida، strace، JADX).
5. توثيق النتائج بالأدلة.

**النتيجة:** عيّنة برمجية خبيثة واحدة قد تستهلك **8–40 ساعة** من وقت محلل خبير. مع **560,000+ عيّنة جديدة يوميًا**، هذا لا يتوسّع.

---

## الحل

> **الهندسة العكسية التقليدية:** تحميل → تنقّل → ربط → توثيق.
>
> **NEXUS-RE:** اسأل سؤالًا. الوكلاء يخطّطون، ينفّذون، ويشرحون — مع دليل لكل ادعاء.

---

## الميزات

### 31 أداة تحليل

| # | الأداة | الفئة | الوصف |
|---|--------|-------|-------|
| 1-6 | Basic | أساسي | hex_dump، strings، hash، entropy، file_info، file_type |
| 7-9 | Format | صيغ | detect_file_type_hex، parse_elf، parse_pe |
| 10-13 | Threat | تهديدات | extract_iocs، scan_apis، detect_packer، yara_scan |
| 14-15 | Crypto | تشفير | xor_v1، xor_v2 |
| 16-21 | Advanced | متقدّم | version_diff، sections، base64، similarity، full_analysis، analyze_file |

### نظام متعدد الوكلاء (4 وكلاء)

| الوكيل | الدور |
|--------|-------|
| **Static Agent** | نوع الملف، تحليل ELF/PE، الـ entropy |
| **Security Agent** | IOCs، APIs مشبوهة، Packers، YARA |
| **Crypto Agent** | XOR brute-force، Base64 |
| **Report Agent** | تجميع الأدلة + الحكم النهائي |

### RAG Service

قاعدة معرفة من **12 مدخلًا**:
- 3 مدخلات NVD/CVE (Log4Shell، Spring4Shell، EternalBlue)
- 5 تقنيات MITRE ATT&CK
- 2 تواقيع Packers
- 2 توثيقات أدوات

### REST API

**24 endpoint** على HTTP Server نقي بلغة Python — بدون أي اعتماديات خارجية.

---

## التثبيت السريع

```bash
git clone https://github.com/qamarsobhy7-source/nexus-re.git
cd nexus-re
python nexus_re_v3.py