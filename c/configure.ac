AC_INIT([declinator], [1.0.1], [arek_koz@o2.pl])
AC_CONFIG_AUX_DIR([.m4/aux])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])
AM_PROG_AR
AC_PROG_CC
AC_CONFIG_MACRO_DIR([.m4/m4])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([
 Makefile
 src/Makefile
])
LT_INIT
PKG_CHECK_MODULES([PCRE], [libpcre >= 1.0])
PKG_CHECK_MODULES([JSON_C], [json-c >= 0.12])
AC_OUTPUT
