use super::{Event as CommitmentEvent, *};
use crate as pallet_commitments;
use frame_support::{
    assert_noop, assert_ok,
    dispatch::Pays,
    parameter_types,
    traits::{ConstU32, ConstU64, GenesisBuild, StorageMapShim},
    Hashable,
};
use frame_system::{EnsureRoot, EventRecord, Phase};
use sp_core::H256;
use sp_runtime::{
    testing::Header,
    traits::{BlakeTwo256, ConstU16, IdentityLookup},
    BuildStorage,
};

pub type Block = sp_runtime::generic::Block<Header, UncheckedExtrinsic>;
pub type UncheckedExtrinsic = sp_runtime::generic::UncheckedExtrinsic<u32, u64, RuntimeCall, ()>;

frame_support::construct_runtime!(
    pub enum Test where
        Block = Block,
        NodeBlock = Block,
        UncheckedExtrinsic = UncheckedExtrinsic
    {
        System: frame_system::{Pallet, Call, Event<T>},
        Balances: pallet_balances,
        Commitments: pallet_commitments
    }
);

#[allow(dead_code)]
pub type AccountId = u64;

// The address format for describing accounts.
#[allow(dead_code)]
pub type Address = AccountId;

// Balance of an account.
#[allow(dead_code)]
pub type Balance = u64;

// An index to a block.
#[allow(dead_code)]
pub type BlockNumber = u64;

impl pallet_balances::Config for Test {
    type Balance = Balance;
    type RuntimeEvent = RuntimeEvent;
    type DustRemoval = ();
    type ExistentialDeposit = ();
    type AccountStore = StorageMapShim<
        pallet_balances::Account<Test>,
        frame_system::Provider<Test>,
        AccountId,
        pallet_balances::AccountData<Balance>,
    >;
    type MaxLocks = ();
    type WeightInfo = ();
    type MaxReserves = ();
    type ReserveIdentifier = ();
}

impl frame_system::Config for Test {
    type BaseCallFilter = frame_support::traits::Everything;
    type BlockWeights = ();
    type BlockLength = ();
    type DbWeight = ();
    type RuntimeOrigin = RuntimeOrigin;
    type RuntimeCall = RuntimeCall;
    type Hash = H256;
    type Hashing = BlakeTwo256;
    type AccountId = u64;
    type Lookup = IdentityLookup<Self::AccountId>;
    type RuntimeEvent = RuntimeEvent;
    type BlockHashCount = ConstU64<250>;
    type Version = ();
    type PalletInfo = PalletInfo;
    type AccountData = ();
    type OnNewAccount = ();
    type OnKilledAccount = ();
    type SystemWeightInfo = ();
    type SS58Prefix = ConstU16<42>;
    type OnSetCode = ();
    type Index = u32;
    type BlockNumber = u64;
    type Header = sp_runtime::generic::Header<Self::BlockNumber, BlakeTwo256>;
    type MaxConsumers = frame_support::traits::ConstU32<16>;
}

impl pallet_commitments::Config for Test {
    type RuntimeEvent = RuntimeEvent;
    type Currency = Balances;
    type WeightInfo = ();
    type MaxFields = frame_support::traits::ConstU32<16>;
    type CanCommit = ();
    type FieldDeposit = frame_support::traits::ConstU64<0>;
    type InitialDeposit = frame_support::traits::ConstU64<0>;
    type RateLimit = frame_support::traits::ConstU64<0>;
}

// Build genesis storage according to the mock runtime.
pub fn new_test_ext() -> sp_io::TestExternalities {
    frame_system::GenesisConfig::default()
        .build_storage::<Test>()
        .unwrap()
        .into()
}
