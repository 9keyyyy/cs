"""
실습 5: 페이징 & 주소 변환 시뮬레이터

Page Table과 TLB를 이용한 논리 주소 → 물리 주소 변환을 구현합니다.
TLB hit/miss 비율을 측정하여 TLB의 효과를 체감합니다.

"""

from collections import OrderedDict

# ============================================================
# 설정
# ============================================================
PAGE_SIZE = 4096  # 4KB
NUM_PAGES = 16    # 가상 주소 공간의 페이지 수
NUM_FRAMES = 8    # 물리 메모리의 프레임 수
TLB_SIZE = 4      # TLB 엔트리 수


# ============================================================
# Page Table Entry
# ============================================================
class PageTableEntry:
    def __init__(self, frame_number: int = -1, valid: bool = False,
                 protection: str = "rw", dirty: bool = False, reference: bool = False):
        self.frame_number = frame_number
        self.valid = valid
        self.protection = protection
        self.dirty = dirty
        self.reference = reference

    def __repr__(self):
        status = "V" if self.valid else "I"
        dirty = "D" if self.dirty else "-"
        return f"[f={self.frame_number:2d} {status}{dirty} {self.protection}]"


# ============================================================
# TLB (Translation Lookaside Buffer)
# ============================================================
class TLB:
    """TLB: 페이지 테이블의 캐시 (LRU 교체)."""

    def __init__(self, size: int):
        self.size = size
        self.entries: OrderedDict[int, int] = OrderedDict()  # page_num → frame_num
        self.hits = 0
        self.misses = 0

    def lookup(self, page_number: int) -> int:
        """
        TLB에서 페이지 번호를 검색합니다.

        Returns: 프레임 번호 (hit) 또는 -1 (miss)
        """
        if page_number in self.entries:
            # TLB hit! 카운터를 증가시키세요.
            self.hits += 1
            # LRU: 최근 사용 항목을 끝으로 이동
            self.entries.move_to_end(page_number)
            return self.entries[page_number]
        else:
            # TLB miss! 카운터를 증가시키세요.
            self.misses += 1
            return -1

    def update(self, page_number: int, frame_number: int):
        """TLB에 새 엔트리를 추가합니다. 꽉 차면 LRU 교체."""
        if page_number in self.entries:
            self.entries.move_to_end(page_number)
            self.entries[page_number] = frame_number
        else:
            # TLB가 꽉 찼으면 가장 오래된 엔트리를 제거하세요.
            if len(self.entries) >= self.size:
                self.entries.popitem(last=False)  # LRU: 가장 처음 항목 제거
            self.entries[page_number] = frame_number

    def flush(self):
        """Context Switch 시 TLB를 비웁니다."""
        self.entries.clear()
        print("  [TLB] Flush 완료 (Context Switch)")

    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def __repr__(self):
        return f"TLB(entries={dict(self.entries)}, hit_ratio={self.hit_ratio():.1%})"


# ============================================================
# MMU (Memory Management Unit)
# ============================================================
class MMU:
    """메모리 관리 장치: 논리 주소 → 물리 주소 변환."""

    def __init__(self):
        self.page_table: list[PageTableEntry] = [PageTableEntry() for _ in range(NUM_PAGES)]
        self.tlb = TLB(TLB_SIZE)
        self.page_faults = 0

        # 일부 페이지를 프레임에 매핑 (초기 상태)
        initial_mapping = {0: 3, 1: 7, 2: 5, 3: 1, 5: 0, 8: 2, 10: 6, 12: 4}
        for page, frame in initial_mapping.items():
            self.page_table[page].frame_number = frame
            self.page_table[page].valid = True

    def translate(self, logical_address: int, access_type: str = "r") -> int:
        """
        논리 주소를 물리 주소로 변환합니다.

        과정:
        1. 논리 주소에서 페이지 번호와 오프셋 추출
        2. TLB 검색
        3. TLB miss → 페이지 테이블 참조
        4. 물리 주소 = 프레임 번호 × 페이지 크기 + 오프셋

        """
        # 페이지 번호와 오프셋을 계산하세요.
        page_number = logical_address // PAGE_SIZE
        offset = logical_address % PAGE_SIZE

        print(f"\n  논리 주소 {logical_address} → 페이지={page_number}, 오프셋={offset}")

        # 1단계: TLB 검색
        frame_number = self.tlb.lookup(page_number)

        if frame_number != -1:
            # TLB Hit
            print(f"  [TLB Hit] 페이지 {page_number} → 프레임 {frame_number}")
        else:
            # TLB Miss → 페이지 테이블 참조
            print(f"  [TLB Miss] 페이지 테이블 참조...")
            pte = self.page_table[page_number]

            # 페이지가 메모리에 있는지 확인하세요. (valid bit)
            if not pte.valid:
                # Page Fault!
                self.page_faults += 1
                print(f"  [Page Fault!] 페이지 {page_number}이 메모리에 없습니다.")
                return -1

            frame_number = pte.frame_number
            pte.reference = True

            if access_type == "w":
                pte.dirty = True

            # TLB를 업데이트하세요.
            self.tlb.update(page_number, frame_number)
            print(f"  [Page Table] 페이지 {page_number} → 프레임 {frame_number}")

        # 물리 주소를 계산하세요.
        physical_address = frame_number * PAGE_SIZE + offset
        print(f"  물리 주소: {physical_address} (프레임={frame_number}, 오프셋={offset})")

        return physical_address

    def print_page_table(self):
        """페이지 테이블을 출력합니다."""
        print(f"\n  {'Page':<6} {'Entry':<25} {'Status':<10}")
        print(f"  {'-'*40}")
        for i, pte in enumerate(self.page_table):
            status = "MEMORY" if pte.valid else "DISK"
            print(f"  {i:<6} {str(pte):<25} {status:<10}")

    def print_stats(self):
        """통계를 출력합니다."""
        print(f"\n  TLB Hit Ratio: {self.tlb.hit_ratio():.1%}")
        print(f"  TLB Hits: {self.tlb.hits}, Misses: {self.tlb.misses}")
        print(f"  Page Faults: {self.page_faults}")


# ============================================================
# Part B: 2단계 페이지 테이블
# ============================================================

class TwoLevelPageTable:
    """
    2단계 페이지 테이블 시뮬레이션.

    32bit 주소, 4KB 페이지:
    - 상위 10bit: Outer Page Table index
    - 중간 10bit: Inner Page Table index
    - 하위 12bit: Offset
    """

    def __init__(self):
        # Outer Table: 1024 엔트리 (대부분 None)
        self.outer_table: list[list[int] | None] = [None] * 1024

    def map_page(self, virtual_page: int, frame: int):
        """가상 페이지를 프레임에 매핑합니다."""
        # outer_index와 inner_index를 계산하세요.
        # 가상 페이지 번호 20bit → 상위 10bit: outer, 하위 10bit: inner
        outer_index = virtual_page // 1024
        inner_index = virtual_page % 1024

        # Inner Table이 없으면 생성
        if self.outer_table[outer_index] is None:
            self.outer_table[outer_index] = [-1] * 1024
            print(f"  [생성] Inner Table #{outer_index}")

        self.outer_table[outer_index][inner_index] = frame

    def lookup(self, virtual_page: int) -> int:
        """가상 페이지의 프레임 번호를 반환합니다."""
        outer_index = virtual_page // 1024
        inner_index = virtual_page % 1024

        if self.outer_table[outer_index] is None:
            return -1  # Inner Table 자체가 없음

        return self.outer_table[outer_index][inner_index]

    def memory_usage(self) -> int:
        """페이지 테이블이 사용하는 메모리(바이트)를 계산합니다."""
        outer_size = 1024 * 4  # Outer Table: 4KB
        inner_count = sum(1 for t in self.outer_table if t is not None)
        inner_size = inner_count * 1024 * 4  # 각 Inner Table: 4KB
        return outer_size + inner_size


# ============================================================
# 메인
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Part A: 페이지 테이블 & TLB 주소 변환")
    print("=" * 60)

    mmu = MMU()
    mmu.print_page_table()

    # 주소 변환 테스트
    test_addresses = [
        (0, "r"),       # Page 0 → Frame 3
        (4096, "r"),    # Page 1 → Frame 7
        (8192, "r"),    # Page 2 → Frame 5
        (0, "r"),       # Page 0 → TLB Hit!
        (4096, "w"),    # Page 1 → TLB Hit!
        (16384, "r"),   # Page 4 → Page Fault!
        (40960, "r"),   # Page 10 → Frame 6
        (0, "r"),       # Page 0 → TLB Hit or Miss?
    ]

    print("\n--- 주소 변환 테스트 ---")
    for addr, access in test_addresses:
        mmu.translate(addr + 100, access)

    mmu.print_stats()

    print("\n" + "=" * 60)
    print("Part B: 2단계 페이지 테이블")
    print("=" * 60)

    two_level = TwoLevelPageTable()

    # 프로세스가 사용하는 가상 주소 영역 (실제로는 극히 일부만 사용)
    # Code: 페이지 0~3, Stack: 페이지 1048572~1048575 (주소 공간 끝)
    mappings = {0: 100, 1: 101, 2: 102, 3: 103,
                1048572: 200, 1048573: 201, 1048574: 202, 1048575: 203}

    print("\n  페이지 매핑:")
    for vp, frame in mappings.items():
        two_level.map_page(vp, frame)
        print(f"  가상 페이지 {vp} → 프레임 {frame}")

    flat_size = 1048576 * 4  # 단일 테이블: 2^20 × 4바이트 = 4MB
    two_level_size = two_level.memory_usage()

    print(f"\n  단일 페이지 테이블 크기: {flat_size:,} bytes ({flat_size/1024:.0f} KB)")
    print(f"  2단계 페이지 테이블 크기: {two_level_size:,} bytes ({two_level_size/1024:.0f} KB)")
    print(f"  메모리 절약: {(1 - two_level_size/flat_size)*100:.1f}%")
