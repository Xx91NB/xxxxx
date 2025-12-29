#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
åˆå§‹åŒ–è„šæœ¬ - ç”¨äºBATæ–‡ä»¶è°ƒç”¨
"""
import sys
import os
from pathlib import Path

def main():
    """ä¸»å‡½æ•°"""
    print("åˆå§‹åŒ–è¾“å‡ºç®¡ç†å™¨...")
    
    try:
        sys.path.append('.')
        from output_manager import get_output_manager
        mgr = get_output_manager()
        print("æ­£ç¡® è¾“å‡ºç®¡ç†å™¨åˆå§‹åŒ–æˆåŠŸ")
        print("è¾“å‡ºæ–‡ä»¶:")
        for name, path in mgr.output_files.items():
            print(f"  - {name}: {path}")
        return 0
    except Exception as e:
        print(f"é”™è¯¯ è¾“å‡ºç®¡ç†å™¨åˆå§‹åŒ–å¤±è´¥: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())try: 
    from output_manager import get_output_manager 
    mgr = get_output_manager() 
    print('ÕıÈ· Êä³ö¹ÜÀíÆ÷³õÊ¼»¯³É¹¦') 
    print('Êä³öÎÄ¼ş:') 
    for name, path in mgr.output_files.items(): 
        print('  -', name, ':', path) 
except Exception as e: 
    print('´íÎó Êä³ö¹ÜÀíÆ÷³õÊ¼»¯Ê§°Ü:', str(e)) 
    import traceback 
    traceback.print_exc() 
    sys.exit(1) 
try: 
    from output_manager import get_output_manager 
    mgr = get_output_manager() 
    print('ÕıÈ· Êä³ö¹ÜÀíÆ÷³õÊ¼»¯³É¹¦') 
    print('Êä³öÎÄ¼ş:') 
    for name, path in mgr.output_files.items(): 
        print('  -', name, ':', path) 
except Exception as e: 
    print('´íÎó Êä³ö¹ÜÀíÆ÷³õÊ¼»¯Ê§°Ü:', str(e)) 
    import traceback 
    traceback.print_exc() 
    sys.exit(1) 
