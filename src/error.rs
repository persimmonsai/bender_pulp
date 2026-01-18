// Copyright (c) 2017 ETH Zurich
// Fabian Schuiki <fschuiki@iis.ee.ethz.ch>

//! Error chaining and reporting facilities.

use std;
use std::fmt;
use std::sync::atomic::AtomicBool;

pub static ENABLE_DEBUG: AtomicBool = AtomicBool::new(false);

/// Print debug information. Omitted in release builds.
#[macro_export]
#[cfg(debug_assertions)]
macro_rules! debugln {
    ($($arg:tt)*) => {
        if $crate::error::ENABLE_DEBUG.load(std::sync::atomic::Ordering::Relaxed) {
            diagnostic!($crate::error::Severity::Debug; $($arg)*);
        }
    }
}

/// Print debug information. Omitted in release builds.
#[macro_export]
#[cfg(not(debug_assertions))]
macro_rules! debugln {
    ($fmt:expr $(, $arg:expr)* $(,)?) => { $(let _ = $arg;)* }
    // create an unused binding here so the compiler does not complain
    // about the arguments to debugln! not being used in release builds.
}

/// Emit a diagnostic message.
macro_rules! diagnostic {
    ($severity:expr; $($arg:tt)*) => {
        eprintln!("{} {}", $severity, format!($($arg)*))
    }
}

/// The severity of a diagnostic message.
#[derive(PartialEq, Eq)]
pub enum Severity {
    Debug,
    Note,
    Warning,
    Error,
}

impl fmt::Display for Severity {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let (color, prefix) = match *self {
            Severity::Error => ("\x1B[31;1m", "error"),
            Severity::Warning => ("\x1B[33;1m", "warning"),
            Severity::Note => ("\x1B[;1m", "note"),
            Severity::Debug => ("\x1B[34;1m", "debug"),
        };
        write!(f, "{}{}:\x1B[m", color, prefix)
    }
}

/// Format and print stage progress.
#[macro_export]
macro_rules! stageln {
    ($stage:expr, $($arg:tt)*) => {
        $crate::error::println_stage($stage, &format!($($arg)*))
    }
}

/// Print stage progress.
pub fn println_stage(stage: &str, message: &str) {
    eprintln!("\x1B[32;1m{:>12}\x1B[0m {}", stage, message);
}
