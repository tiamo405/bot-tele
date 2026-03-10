#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for AI handler
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from get_api.ai import ask_ai

def test_ai_questions():
    """Test các câu hỏi mẫu"""
    
    test_cases = [
        {
            "title": "Câu hỏi giải thích khái niệm",
            "question": "Giải thích ngắn gọn về blockchain"
        },
        {
            "title": "Viết code Python",
            "question": "Viết code Python tính số fibonacci thứ n"
        },
        {
            "title": "So sánh công nghệ",
            "question": "Sự khác biệt giữa list và tuple trong Python"
        }
    ]
    
    print("=" * 80)
    print("TEST AI HANDLER - GEMINI 2.5 FLASH")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test['title']}")
        print(f"{'='*80}")
        print(f"❓ QUESTION: {test['question']}")
        print(f"\n🤖 ANSWER:")
        print("-" * 80)
        
        answer = ask_ai(test['question'])
        print(answer)
        print("-" * 80)
        print(f"✅ Length: {len(answer)} characters")
    
    print(f"\n{'='*80}")
    print("✅ ALL TESTS COMPLETED")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    test_ai_questions()
