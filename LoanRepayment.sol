// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * LoanRepayment.sol
 * Blockchain Dynamic Interest Rate System — Data Layer
 *
 * Blockchain properties used:
 *   - Tamper-resistant : records are immutable once written
 *   - Time-stamping    : block.timestamp records exact repayment time
 *   - Transparency     : all institutions read the same ledger
 *   - Non-repudiation  : msg.sender proves who submitted the record
 */
contract LoanRepayment {

    // ── Data structures ──────────────────────────────────────────────────────

    struct Repayment {
        address borrower;       // wallet address = borrower identity
        address institution;    // bank / lender that submitted this record
        uint256 amount;         // repayment amount in wei (or smallest unit)
        uint256 timestamp;      // block timestamp (Unix seconds)
        bool    onTime;         // was this repayment made on or before due date?
        uint256 dueDate;        // expected repayment date (Unix timestamp)
    }

    struct BorrowerProfile {
        uint256 totalRepayments;
        uint256 onTimeRepayments;
        uint256 lateRepayments;
        uint256 firstRepaymentTime;
        uint256 lastRepaymentTime;
    }

    // ── Storage ───────────────────────────────────────────────────────────────

    // All repayment records, indexed globally
    Repayment[] public repayments;

    // borrower address => list of their repayment indices
    mapping(address => uint256[]) public borrowerRepayments;

    // borrower address => aggregated profile stats
    mapping(address => BorrowerProfile) public borrowerProfiles;

    // Approved institutions that may submit records (access control)
    mapping(address => bool) public approvedInstitutions;

    address public owner;

    // ── Events (emitted on-chain, readable by ML layer / frontend) ────────────

    event RepaymentRecorded(
        uint256 indexed repaymentId,
        address indexed borrower,
        address indexed institution,
        uint256 amount,
        uint256 timestamp,
        bool    onTime
    );

    event InstitutionApproved(address indexed institution);
    event InstitutionRevoked(address indexed institution);

    // ── Modifiers ─────────────────────────────────────────────────────────────

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    modifier onlyApprovedInstitution() {
        require(approvedInstitutions[msg.sender], "Institution not approved");
        _;
    }

    // ── Constructor ───────────────────────────────────────────────────────────

    constructor() {
        owner = msg.sender;
        // Owner is auto-approved as the first institution (for demo purposes)
        approvedInstitutions[msg.sender] = true;
    }

    // ── Institution management (owner only) ───────────────────────────────────

    function approveInstitution(address _institution) external onlyOwner {
        approvedInstitutions[_institution] = true;
        emit InstitutionApproved(_institution);
    }

    function revokeInstitution(address _institution) external onlyOwner {
        approvedInstitutions[_institution] = false;
        emit InstitutionRevoked(_institution);
    }

    // ── Core: record a repayment ──────────────────────────────────────────────

    /**
     * @param _borrower   The borrower's wallet address
     * @param _amount     Repayment amount
     * @param _dueDate    Unix timestamp of when payment was due
     * @param _onTime     Whether the borrower paid on or before due date
     */
    function recordRepayment(
        address _borrower,
        uint256 _amount,
        uint256 _dueDate,
        bool    _onTime
    ) external onlyApprovedInstitution {
        uint256 id = repayments.length;

        repayments.push(Repayment({
            borrower:    _borrower,
            institution: msg.sender,
            amount:      _amount,
            timestamp:   block.timestamp,
            onTime:      _onTime,
            dueDate:     _dueDate
        }));

        borrowerRepayments[_borrower].push(id);

        // Update aggregated profile (used by ML feature calculation)
        BorrowerProfile storage profile = borrowerProfiles[_borrower];
        profile.totalRepayments++;
        if (_onTime) {
            profile.onTimeRepayments++;
        } else {
            profile.lateRepayments++;
        }
        if (profile.firstRepaymentTime == 0) {
            profile.firstRepaymentTime = block.timestamp;
        }
        profile.lastRepaymentTime = block.timestamp;

        emit RepaymentRecorded(id, _borrower, msg.sender, _amount, block.timestamp, _onTime);
    }

    // ── Read functions (called by ML layer / frontend) ────────────────────────

    function getRepayment(uint256 _id) external view returns (Repayment memory) {
        require(_id < repayments.length, "Invalid ID");
        return repayments[_id];
    }

    function getBorrowerRepaymentIds(address _borrower)
        external view returns (uint256[] memory)
    {
        return borrowerRepayments[_borrower];
    }

    function getBorrowerProfile(address _borrower)
        external view returns (BorrowerProfile memory)
    {
        return borrowerProfiles[_borrower];
    }

    function totalRepayments() external view returns (uint256) {
        return repayments.length;
    }

    /**
     * Calculate on-time rate for a borrower (0–100)
     * Used as a derived feature for the ML model
     */
    function getOnTimeRate(address _borrower) external view returns (uint256) {
        BorrowerProfile memory p = borrowerProfiles[_borrower];
        if (p.totalRepayments == 0) return 0;
        return (p.onTimeRepayments * 100) / p.totalRepayments;
    }
}
